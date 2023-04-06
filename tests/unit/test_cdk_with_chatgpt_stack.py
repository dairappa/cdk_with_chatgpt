import re
import pytest
import aws_cdk as core
from aws_cdk.aws_s3 import Bucket
from constructs import Construct

from cdk_with_chatgpt.cdk_with_chatgpt_stack import CdkWithChatgptStack



def get_stack() -> CdkWithChatgptStack:
    app = core.App()
    return CdkWithChatgptStack(app, "MyTestStack")


def test_stack_has_bucket():
    stack = get_stack()
    assert stack.destination_bucket is not None, "Expected a Bucket in the stack"

def test_bucket_name():
    app = core.App()
    stack = CdkWithChatgptStack(app, "MyTestStack")
    template = app.synth().get_stack_by_name("MyTestStack").template

    # Find the AWS::S3::Bucket resource in the template
    bucket_resource = None
    for _, resource in template['Resources'].items():
        if resource['Type'] == 'AWS::S3::Bucket':
            bucket_resource = resource
            break

    assert bucket_resource is not None, "Expected a Bucket resource in the template"

    # Check the bucket name
    bucket_name_fn_join = bucket_resource['Properties']['BucketName']
    assert bucket_name_fn_join["Fn::Join"][1][0] == "destination-", \
        f"Expected bucket name to start with 'destination-', but got '{bucket_name_fn_join}'"


def test_bucket_properties():
    app = core.App()
    stack = CdkWithChatgptStack(app, "MyTestStack")
    template = app.synth().get_stack_by_name("MyTestStack").template

    # Find the AWS::S3::Bucket resource in the template
    bucket_resource = None
    for _, resource in template['Resources'].items():
        if resource['Type'] == 'AWS::S3::Bucket':
            bucket_resource = resource
            break

    assert bucket_resource is not None, "Expected a Bucket resource in the template"

    # Check block public access settings
    block_public_access = bucket_resource['Properties']['PublicAccessBlockConfiguration']
    assert block_public_access == {
        'BlockPublicAcls': True,
        'BlockPublicPolicy': True,
        'IgnorePublicAcls': True,
        'RestrictPublicBuckets': True
    }, "Expected public access to be blocked for the Bucket"

    # Check removal policy
    assert bucket_resource['DeletionPolicy'] == 'Delete', "Expected removal policy to be Delete"

    # Check versioning
    assert bucket_resource['Properties']['VersioningConfiguration']['Status'] == 'Enabled', \
        "Expected Bucket to have versioning enabled"
