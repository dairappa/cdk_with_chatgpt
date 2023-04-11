from aws_cdk import RemovalPolicy, Stack
import aws_cdk as core
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_ecr import Repository
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk.aws_ecs import ContainerImage
from aws_cdk.aws_sqs import Queue, DeadLetterQueue

class CdkWithChatgptStack(Stack):

    destination_bucket: Bucket
    ecr_repository: Repository
    docker_image_asset: DockerImageAsset
    container_image: ContainerImage
    task_queue: Queue
    dlq_for_task_queue: Queue

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


