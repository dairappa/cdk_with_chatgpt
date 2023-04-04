from aws_cdk import RemovalPolicy, Stack, aws_s3 as s3
from constructs import Construct

class CdkWithChatgptStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an Amazon S3 bucket
        s3.Bucket(self, "MyBucket", versioned=True, removal_policy=RemovalPolicy.DESTROY)


