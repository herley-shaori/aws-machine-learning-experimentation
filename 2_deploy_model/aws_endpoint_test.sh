aws sagemaker-runtime invoke-endpoint \
    --endpoint-name MyModelEndpoint \
    --body '[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]]' \
    --content-type application/json \
    --region ap-southeast-3 \
    output.json