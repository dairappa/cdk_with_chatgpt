import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_with_chatgpt.cdk_with_chatgpt_stack import CdkWithChatgptStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_with_chatgpt/cdk_with_chatgpt_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkWithChatgptStack(app, "cdk-with-chatgpt")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
