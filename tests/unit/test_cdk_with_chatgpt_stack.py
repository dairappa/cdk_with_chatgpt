import aws_cdk as core
import pytest

from cdk_with_chatgpt.cdk_with_chatgpt_stack import CdkWithChatgptStack


# This is a helper function to get the Bucket resource from the stack
def get_bucket_resource_from_stack():
    app = core.App()
    CdkWithChatgptStack(app, "MyTestStack")
    template = app.synth().get_stack_by_name("MyTestStack").template
    for _, resource in template['Resources'].items():
        if resource['Type'] == 'AWS::S3::Bucket':
            return resource
    return None

def test_bucket_name():
    bucket_resource = get_bucket_resource_from_stack()
    assert bucket_resource is not None, "Expected a Bucket resource in the template"

    # Check the bucket name
    bucket_name_fn_join = bucket_resource['Properties']['BucketName']
    assert bucket_name_fn_join["Fn::Join"][1][0] == "destination-", \
        f"Expected bucket name to start with 'destination-', but got '{bucket_name_fn_join}'"

# test for block public access settings, removal policy, and versioning
def test_bucket_properties():
    bucket_resource = get_bucket_resource_from_stack()
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
