#!/bin/bash

# Deploy the CDK stack
cdk deploy --all --require-approval never
if [ $? -ne 0 ]; then
  echo "Error: CDK deployment failed."
  exit 1
fi

# Retrieve the S3 bucket name from the stack output using ExportName
STACK_NAME="DeployExternalModelToSagemakerRealtimeEndpoint"
echo "Fetching outputs for stack: $STACK_NAME"
aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs" --output json

BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?ExportName=='ModelBucketName'].OutputValue" --output text 2>/dev/null)

# Check if BUCKET_NAME is empty or unset
if [ -z "$BUCKET_NAME" ]; then
  echo "Error: Could not retrieve bucket name. Verify that the stack '$STACK_NAME' includes an output with ExportName 'ModelBucketName'."
  exit 1
fi

# Verify the model file exists
MODEL_FILE="../1_model_creation/random_forest_model.pkl"
if [ ! -f "$MODEL_FILE" ]; then
  echo "Error: Model file '$MODEL_FILE' not found."
  exit 1
fi

# Upload the model file to the S3 bucket
aws s3 cp "$MODEL_FILE" "s3://$BUCKET_NAME/random_forest_model.pkl"
if [ $? -eq 0 ]; then
  echo "Model file uploaded to s3://$BUCKET_NAME/random_forest_model.pkl"
else
  echo "Error: Failed to upload model file to s3://$BUCKET_NAME/random_forest_model.pkl"
  exit 1
fi