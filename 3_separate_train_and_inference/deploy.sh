#!/bin/bash

set -e

# Deploy CDK stack
echo "Deploying CDK stack..."
cdk deploy --require-approval never