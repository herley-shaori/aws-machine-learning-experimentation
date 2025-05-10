#!/bin/bash

# Ensure jq is installed
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required to parse parameters.json. Please install jq."
  exit 1
fi

# Read StackName from parameters.json
PARAMETERS_FILE="parameters.json"
STACK_NAME=$(jq -r '.[] | select(.ParameterKey=="StackName") | .ParameterValue' $PARAMETERS_FILE)

if [ -z "$STACK_NAME" ]; then
  echo "Error: Could not retrieve StackName from $PARAMETERS_FILE"
  exit 1
fi

TEMPLATE_FILE="file://infra.yaml"
PARAMETERS_FILE="file://parameters.json"

# Check if the stack already exists
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" >/dev/null 2>&1; then
  echo "Stack $STACK_NAME exists, attempting to update..."
  aws cloudformation update-stack \
    --stack-name "$STACK_NAME" \
    --template-body "$TEMPLATE_FILE" \
    --parameters "$PARAMETERS_FILE" \
    --capabilities CAPABILITY_NAMED_IAM
  echo "Update stack command issued."
else
  echo "Stack $STACK_NAME does not exist, creating..."
  aws cloudformation create-stack \
    --stack-name "$STACK_NAME" \
    --template-body "$TEMPLATE_FILE" \
    --parameters "$PARAMETERS_FILE" \
    --capabilities CAPABILITY_NAMED_IAM
  echo "Create stack command issued."
fi