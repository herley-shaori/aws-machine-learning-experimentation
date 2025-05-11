#!/bin/zsh

# Create the input JSON file
cat > input.json << 'EOF'
[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]]
EOF

# Invoke the SageMaker endpoint
aws sagemaker-runtime invoke-endpoint \
    --endpoint-name MyModelEndpointx \
    --body file://input.json \
    --content-type application/json \
    --region ap-southeast-3 \
    --cli-binary-format raw-in-base64-out \
    output.json

cat output.json