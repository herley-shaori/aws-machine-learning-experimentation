#!/usr/bin/env python3
import aws_cdk as cdk
from deploy_model.deploy_model_stack import DeployModelStack

app = cdk.App()
DeployModelStack(app, "DeployModelStack")
app.synth()