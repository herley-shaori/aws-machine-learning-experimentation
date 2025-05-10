#!/bin/bash

# Default values for flags
UPLOAD_TO_S3=false
RUN_CODEBUILD=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --upload-to-s3)
            UPLOAD_TO_S3="$2"
            shift 2
            ;;
        --run-codebuild)
            RUN_CODEBUILD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to upload zip to S3
upload_to_s3() {
    echo "Zipping contents of 1_model_creation folder, excluding .venv"
    cd ../1_model_creation
    zip -r model_creation.zip . -x ".venv/*" -x ".venv"
    cd ../2_deploy_external_model_to_sagemaker_realtime_endpoint

    # Get the S3 bucket name from CloudFormation stack outputs
    BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name DeployExternalModelToSagemakerRealtimeEndpoint --query "Stacks[0].Outputs[?ExportName=='ModelBucketName'].OutputValue" --output text)

    # Check if BUCKET_NAME is empty
    if [ -z "$BUCKET_NAME" ]; then
        echo "Error: Failed to retrieve S3 bucket name from CloudFormation outputs"
        exit 1
    fi

    # Upload the zip file to the S3 bucket
    echo "Uploading model_creation.zip to S3 bucket: $BUCKET_NAME"
    aws s3 cp ../1_model_creation/model_creation.zip s3://$BUCKET_NAME/model_creation.zip
    if [ $? -ne 0 ]; then
        echo "Error: Failed to upload model_creation.zip to S3 bucket $BUCKET_NAME"
        exit 1
    fi
}

# Function to run CodeBuild
run_codebuild() {
    # Get the CodeBuild project name from CloudFormation stack outputs
    CODEBUILD_PROJECT_NAME=$(aws cloudformation describe-stacks --stack-name DeployExternalModelToSagemakerRealtimeEndpoint --query "Stacks[0].Outputs[?ExportName=='CodeBuildProjectName'].OutputValue" --output text)

    # Check if CODEBUILD_PROJECT_NAME is empty
    if [ -z "$CODEBUILD_PROJECT_NAME" ]; then
        echo "Error: Failed to retrieve CodeBuild project name from CloudFormation outputs"
        exit 1
    fi

    # Trigger the CodeBuild project and extract build ID
    echo "Starting CodeBuild project: $CODEBUILD_PROJECT_NAME"
    BUILD_INFO=$(aws codebuild start-build --project-name "$CODEBUILD_PROJECT_NAME" --no-cli-pager --query '{BuildId: build.id, ProjectName: build.projectName}' --output json)
    BUILD_ID=$(echo "$BUILD_INFO" | jq -r '.BuildId')

    # Check if BUILD_ID is empty
    if [ -z "$BUILD_ID" ]; then
        echo "Error: Failed to retrieve build ID from CodeBuild"
        exit 1
    fi

    echo "CodeBuild started successfully. Build ID: $BUILD_ID"
}

# Deploy the CDK stack
echo "Deploying CDK stack"
cdk deploy --all --require-approval never
if [ $? -ne 0 ]; then
    echo "Error: CDK deployment failed"
    exit 1
fi

# Execute S3 upload if enabled
if [ "$UPLOAD_TO_S3" = "true" ]; then
    upload_to_s3
else
    echo "Skipping S3 upload (upload-to-s3=false)"
fi

# Execute CodeBuild if enabled
if [ "$RUN_CODEBUILD" = "true" ]; then
    run_codebuild
else
    echo "Skipping CodeBuild execution (run-codebuild=false)"
fi