import aws_cdk as core
import aws_cdk.assertions as assertions

from 3_deploy_realtime_endpoint_from_notebook.3_deploy_realtime_endpoint_from_notebook_stack import 3DeployRealtimeEndpointFromNotebookStack

# example tests. To run these tests, uncomment this file along with the example
# resource in 3_deploy_realtime_endpoint_from_notebook/3_deploy_realtime_endpoint_from_notebook_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 3DeployRealtimeEndpointFromNotebookStack(app, "3-deploy-realtime-endpoint-from-notebook")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
