#!/bin/bash

# Deploy the CDK stack
cdk deploy --all --require-approval never

# Zip the contents of 1_model_creation folder, excluding .venv
cd ../1_model_creation
zip -r model_creation.zip . -x ".venv/**"
cd ../2_deploy_external_model_to_sagemaker_realtime_endpoint

# Get the S3 bucket name from CloudFormation stack outputs
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name DeployExternalModelToSagemakerRealtimeEndpoint --query "Stacks[0].Outputs[?OutputKey=='ModelBucketName'].OutputValue" --output text)

# Upload the zip file to the S3 bucket
aws s3 cp ../1_model_creation/model_creation.zip s3://$BUCKET_NAME/model_creation.zip