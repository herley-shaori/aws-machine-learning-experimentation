#!/bin/bash

# Exit on any error
set -e

# Bootstrap CDK with a custom S3 bucket name
echo "Bootstrapping CDK..."
cdk bootstrap
# Deploy the CDK stack
echo "Deploying CDK stack..."
cdk deploy --require-approval never

echo "Deployment completed successfully."