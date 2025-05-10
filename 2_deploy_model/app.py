#!/usr/bin/env python3
import aws_cdk as cdk
from deploy_model.deploy_model_stack import DeployModelStack

app = cdk.App()
env = cdk.Environment(region="ap-southeast-3")
DeployModelStack(app, "DeployModelStack", env=env)
app.synth()