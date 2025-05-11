#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deploy_realtime_endpoint_from_notebook.deploy_realtime_endpoint_from_notebook_stack import DeployRealtimeEndpointFromNotebookStack


app = cdk.App()
DeployRealtimeEndpointFromNotebookStack(app, "DeployRealtimeEndpointFromNotebookStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION")
    )
)
app.synth()
