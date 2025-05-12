import boto3
from sagemaker.model import Model
from sagemaker import Session

# Initialize SageMaker session and client
boto_session = boto3.Session(region_name='ap-southeast-3')
sagemaker_session = Session(boto_session=boto_session)
sagemaker_client = boto3.client('sagemaker', region_name='ap-southeast-3')

# Model ARN
model_arn = 'arn:aws:sagemaker:ap-southeast-3:623127157773:model/sklearn-model-2025-05-12-08-29-54'

# Custom VPC configuration
subnets = ['subnet-0c20b14a7dd88fb72', 'subnet-003c9aa1cc5a12451']
security_group_ids = ['sg-03f6f1e8d4441f4f7']

# Describe the model to get its details
model_desc = sagemaker_client.describe_model(ModelName=model_arn.split('/')[-1])
model_data_url = model_desc['PrimaryContainer']['ModelDataUrl']
image_uri = model_desc['PrimaryContainer']['Image']
role_arn = model_desc['ExecutionRoleArn']

# Create a Model object
model = Model(
    model_data=model_data_url,
    image_uri=image_uri,
    role=role_arn,
    sagemaker_session=sagemaker_session
)

# Deploy model to a SageMaker endpoint with VPC settings
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.2xlarge',
    endpoint_name='sklearn-linear-regression-endpoint',
    vpc_config={
        'Subnets': subnets,
        'SecurityGroupIds': security_group_ids
    }
)

print(f"Model deployed to endpoint: sklearn-linear-regression-endpoint")