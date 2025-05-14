# sagemaker_dev/code.py
import boto3
import sagemaker
from sagemaker.sklearn import SKLearn
import numpy as np
import pandas as pd

# 1) Generate synthetic data
np.random.seed(42)
n_samples = 100
feature1 = np.random.uniform(0, 10, n_samples)
feature2 = np.random.uniform(0, 10, n_samples)
feature3 = np.random.uniform(0, 10, n_samples)
target   = 2 * feature1 + 3 * feature2 + 4 * feature3 + np.random.normal(0, 1, n_samples)

df = pd.DataFrame({
    'feature1': feature1,
    'feature2': feature2,
    'feature3': feature3,
    'target':   target
})
df.to_csv('train.csv', index=False)

# 2) Upload to S3
bucket = 'sagemaker-ap-southeast-3-623127157773'
s3_path = 'data/train.csv'
boto3.client('s3', region_name='ap-southeast-3') \
      .upload_file('train.csv', bucket, s3_path)
s3_uri = f's3://{bucket}/{s3_path}'
print(f"Uploaded train.csv to {s3_uri}")

# 3) Configure and run the SKLearn estimator using train.py
boto_sess = boto3.Session(region_name='ap-southeast-3')
sm_sess   = sagemaker.Session(boto_session=boto_sess)

output_path = f's3://{bucket}/output'
sklearn_estimator = SKLearn(
    entry_point='train.py',       # <-- training script
    source_dir='entrypoint',      # contains train.py
    role='arn:aws:iam::623127157773:role/DeployRealtimeEndpointFromNote-NotebookRoleCDEC1E3A-87HCGqVQrP0t',
    instance_type='ml.m5.4xlarge',
    framework_version='0.23-1',
    py_version='py3',
    output_path=output_path,
    sagemaker_session=sm_sess
)

sklearn_estimator.fit({'train': s3_uri})
print("Training complete:", sklearn_estimator.latest_training_job.name)
