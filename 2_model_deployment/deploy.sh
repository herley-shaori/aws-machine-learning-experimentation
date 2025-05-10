aws cloudformation update-stack \
  --stack-name MyNetworkStack \
  --template-body file://infra.yaml \
  --parameters file://parameters.json