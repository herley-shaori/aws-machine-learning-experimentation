#!/bin/bash

# Deploy the CDK stack
cdk deploy --all --require-approval never
if [ $? -ne 0 ]; then
    echo "Error: CDK deployment failed."
    exit 1
fi

# Retrieve the S3 bucket name
STACK_NAME="DeployExternalModelToSagemakerRealtimeEndpoint"
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?ExportName=='ModelBucketName'].OutputValue" --output text 2>/dev/null)

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: Could not retrieve bucket name."
    exit 1
fi

# Verify model and inference script
MODEL_FILE="../1_model_creation/random_forest_model.pkl"
INFERENCE_SCRIPT="../1_model_creation/inference.py"
if [ ! -f "$MODEL_FILE" ] || [ ! -f "$INFERENCE_SCRIPT" ]; then
    echo "Error: Model file or inference script not found."
    exit 1
fi

# Package model and inference code
MODEL_DIR="model_package"
mkdir -p "$MODEL_DIR"
cp "$MODEL_FILE" "$MODEL_DIR/"
cp "$INFERENCE_SCRIPT" "$MODEL_DIR/"
tar -czf "model.tar.gz" -C "$MODEL_DIR" .
rm -rf "$MODEL_DIR"

# Upload to S3
aws s3 cp "model.tar.gz" "s3://$BUCKET_NAME/model.tar.gz"
if [ $? -eq 0 ]; then
    echo "Model package uploaded to s3://$BUCKET_NAME/model.tar.gz"
else
    echo "Error: Failed to upload model package."
    exit 1
fi