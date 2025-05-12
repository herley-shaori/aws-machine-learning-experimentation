import boto3
import datetime

# Initialize SageMaker client
sagemaker_client = boto3.client('sagemaker', region_name='ap-southeast-3')

# Training job ARN
training_job_arn = 'arn:aws:sagemaker:ap-southeast-3:623127157773:training-job/sagemaker-scikit-learn-2025-05-12-01-22-24-222'

# Custom VPC configuration
subnets = ['subnet-0c20b14a7dd88fb72', 'subnet-003c9aa1cc5a12451']
security_group_ids = ['sg-03f6f1e8d4441f4f7']

# Extract training job name from ARN
training_job_name = training_job_arn.split('/')[-1]

# Describe the training job to get model artifacts and role
training_job_desc = sagemaker_client.describe_training_job(TrainingJobName=training_job_name)
model_data_url = training_job_desc['ModelArtifacts']['S3ModelArtifacts']
role_arn = training_job_desc['RoleArn']
training_image = training_job_desc['AlgorithmSpecification']['TrainingImage']

# Create SageMaker model with VPC configuration
model_name = f"sklearn-model-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
sagemaker_client.create_model(
    ModelName=model_name,
    PrimaryContainer={
        'Image': training_image,
        'ModelDataUrl': model_data_url
    },
    ExecutionRoleArn=role_arn,
    VpcConfig={
        'Subnets': subnets,
        'SecurityGroupIds': security_group_ids
    }
)

print(f"Model created with name: {model_name}")