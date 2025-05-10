import aws_cdk as core
import aws_cdk.assertions as assertions

from 2_deploy_model.2_deploy_model_stack import 2DeployModelStack

# example tests. To run these tests, uncomment this file along with the example
# resource in 2_deploy_model/2_deploy_model_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 2DeployModelStack(app, "2-deploy-model")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
