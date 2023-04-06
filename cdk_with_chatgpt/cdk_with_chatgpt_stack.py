from aws_cdk import RemovalPolicy, Stack
import aws_cdk as core
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess


class CdkWithChatgptStack(Stack):

    destination_bucket: Bucket


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


