#!/bin/bash

# Exit on any error
set -e

# Destroy the CDK stack
echo "Destroying CDK stack..."
cdk destroy --force

echo "Stack destruction completed successfully."