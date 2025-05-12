import sagemaker
import boto3
from sagemaker.sklearn.estimator import SKLearn

# Initialize SageMaker session
boto_session = boto3.Session(region_name='ap-southeast-3')
sagemaker_session = sagemaker.Session(boto_session=boto_session)

# Corrected training job name from ARN
training_job_name = 'sagemaker-scikit-learn-2025-05-12-08-56-18-084'

# Attach to the existing training job
estimator = SKLearn.attach(training_job_name=training_job_name, sagemaker_session=sagemaker_session)

# Custom VPC configuration
subnets = ['subnet-0c20b14a7dd88fb72', 'subnet-003c9aa1cc5a12451']
security_group_ids = ['sg-03f6f1e8d4441f4f7']

# Deploy model to a SageMaker endpoint with VPC settings
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.2xlarge',
    endpoint_name='sklearn-linear-regression-endpoint-kj78',
    # vpc_config={
    #     'Subnets': subnets,
    #     'SecurityGroupIds': security_group_ids
    # }
)

print(f"Model deployed to endpoint: sklearn-linear-regression-endpoint-89hjk")