#!/bin/bash

set -e

# Bootstrap CDK
echo "Bootstrapping CDK..."
cdk bootstrap

# Deploy CDK stack
echo "Deploying CDK stack..."
cdk deploy --require-approval never

# Get bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name DeployModelStack --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)

# Upload files to S3
#echo "Uploading code.zip and model.tar.gz to S3..."
#aws s3 cp ../1_model_creation/model_creation.zip s3://$BUCKET_NAME/model_creation.zip

# Get CodeBuild project name
CODEBUILD_PROJECT=$(aws cloudformation describe-stacks --stack-name DeployModelStack --query "Stacks[0].Outputs[?OutputKey=='CodeBuildProjectName'].OutputValue" --output text)

# Start CodeBuild project
#echo "Starting CodeBuild project..."
#aws codebuild start-build --project-name $CODEBUILD_PROJECT
#echo "Deployment completed successfully."