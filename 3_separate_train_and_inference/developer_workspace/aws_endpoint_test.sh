#!/bin/zsh

cat > input.json << 'EOF'
[[1.0, 2.0, 3.0]]
EOF

aws sagemaker-runtime invoke-endpoint \
    --endpoint-name sklearn-linear-regression-endpoint-sm2 \
    --body file://input.json \
    --content-type application/json \
    --accept application/json \
    --region ap-southeast-3 \
    --cli-binary-format raw-in-base64-out \
    output.json

cat output.json