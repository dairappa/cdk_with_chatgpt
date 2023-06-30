from aws_cdk import RemovalPolicy, Stack
import aws_cdk as core
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_ecr import Repository
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk.aws_sqs import Queue, DeadLetterQueue
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
from aws_cdk.aws_ecs import ContainerImage, FargateTaskDefinition, LogDriver, FargatePlatformVersion, ContainerDefinition, PortMapping, Cluster
from aws_cdk.aws_ecs_patterns import ScheduledFargateTask
from aws_cdk.aws_applicationautoscaling import Schedule
from aws_cdk.aws_iam import PolicyStatement, Role, ServicePrincipal
from aws_cdk.aws_ec2 import Vpc


class CdkWithChatgptStack(Stack):

    destination_bucket: Bucket
    ecr_repository: Repository
    docker_image_asset: DockerImageAsset
    container_image: ContainerImage
    task_queue: Queue
    dlq_for_task_queue: Queue
    ecs_task_role: Role
    task_definition: FargateTaskDefinition
    task_container: ContainerDefinition
    scheduled_task: ScheduledFargateTask

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_account_id = core.Aws.ACCOUNT_ID
        bucket_name = f"destination-{my_account_id}"

        self.destination_bucket = Bucket(self, "DestinationBucket",
            bucket_name=bucket_name,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            versioned=True,
        )

        docker_directory = './docker'

        self.ecr_repository = Repository(self, 'EcrRepository')

        self.docker_image_asset = DockerImageAsset(self, 'DockerImage', directory=docker_directory,)

        self.container_image = ContainerImage.from_asset(docker_directory)

        self.dlq_for_task_queue = Queue(self, "CopyDataTaskDeadLetterQueue",
            queue_name=f"copy-data-task-dlq-{my_account_id}"
        )

        self.task_queue = Queue(self, "CopyDataTaskQueue",
            queue_name=f"copy-data-task-queue-{my_account_id}",
            dead_letter_queue=DeadLetterQueue(max_receive_count=3, queue=self.dlq_for_task_queue)
        )

        # IAM role for the ECS task
        self.ecs_task_role = Role(self, 'ECSTaskRole',
            assumed_by=ServicePrincipal('ecs-tasks.amazonaws.com'),
        )

        # Add permissions for S3 and SQS
        self.ecs_task_role.add_to_policy(PolicyStatement(
            actions=[
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
            ],
            resources=[f"{self.destination_bucket.bucket_arn}/*"]
        ))

        self.ecs_task_role.add_to_policy(PolicyStatement(
            actions=[
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
            ],
            resources=[self.task_queue.queue_arn]
        ))

        # ECS Fargate task definition
        self.task_definition = FargateTaskDefinition(self, 'TaskDef',
            memory_limit_mib=512,
            cpu=256,
            task_role=self.ecs_task_role,  # type: ignore
        )

        self.task_container = self.task_definition.add_container('Container',
            image=self.container_image,
            logging=LogDriver.aws_logs(stream_prefix='ecs'),
            environment={
                'S3_BUCKET_NAME': self.destination_bucket.bucket_name,
                'SQS_QUEUE_URL': self.task_queue.queue_url,
            }
        )

        self.task_container.add_port_mappings(PortMapping(container_port=80))

        # Fetch the VPC ARN from context
        vpc_arn = self.node.try_get_context('vpc_arn')
        vpc_id = vpc_arn.split(':')[-1].split('/')[-1]

        # Import the VPC using the Vpc.from_vpc_attributes() method
        vpc = Vpc.from_lookup(self, 'ImportedVPC', vpc_id=vpc_id)

        # Create the ECS cluster
        ecs_cluster = Cluster(self, 'ECSCluster',
            vpc=vpc,  # type: ignore
        )







        


