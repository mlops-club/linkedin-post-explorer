import aws_cdk as core
import aws_cdk.assertions as assertions

from linkedin_post_explorer.linkedin_post_explorer_stack import LinkedinPostExplorerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in linkedin_post_explorer/linkedin_post_explorer_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LinkedinPostExplorerStack(app, "linkedin-post-explorer")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
