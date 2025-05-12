import boto3
import sagemaker
from sagemaker.sklearn import SKLearn
import numpy as np
import pandas as pd

# Generate synthetic data for train.csv
np.random.seed(42)
n_samples = 100
feature1 = np.random.uniform(0, 10, n_samples)
feature2 = np.random.uniform(0, 10, n_samples)
feature3 = np.random.uniform(0, 10, n_samples)
target = 2 * feature1 + 3 * feature2 + 4 * feature3 + np.random.normal(0, 1, n_samples)

# Create DataFrame
data = pd.DataFrame({
    'feature1': feature1,
    'feature2': feature2,
    'feature3': feature3,
    'target': target
})

# Save to train.csv locally
local_path = 'train.csv'
data.to_csv(local_path, index=False)

# Upload train.csv to S3
bucket = 'deployrealtimeendpointfrom-sagemakerbucket4e4a68ec-v7m7t5plnagp'
s3_path = 'data/train.csv'
s3_uri = f's3://{bucket}/{s3_path}'

s3_client = boto3.client('s3', region_name='ap-southeast-3')
s3_client.upload_file(local_path, bucket, s3_path)
print(f"Uploaded {local_path} to {s3_uri}")

# Configure SageMaker session for cloud execution in ap-southeast-3
boto_session = boto3.Session(region_name='ap-southeast-3')
sagemaker_session = sagemaker.Session(boto_session=boto_session)

# Define S3 output path for model artifacts
output_path = f's3://{bucket}/output'

# VPC configuration
subnets = ['subnet-0c20b14a7dd88fb72', 'subnet-003c9aa1cc5a12451']
security_group_ids = ['sg-03f6f1e8d4441f4f7']

# Create SKLearn estimator with VPC configuration
sklearn_estimator = SKLearn(
    entry_point='train.py',
    role='arn:aws:iam::623127157773:role/DeployRealtimeEndpointFromNote-NotebookRoleCDEC1E3A-PvEOUXSxbiNF',
    instance_type='ml.m5.2xlarge',
    framework_version='0.23-1',
    py_version='py3',
    output_path=output_path
)

sklearn_estimator.fit({'train': s3_uri})
print(f"Training job completed: {sklearn_estimator.latest_training_job.name}")