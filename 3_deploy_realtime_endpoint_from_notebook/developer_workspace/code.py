import boto3
import sagemaker
from sagemaker.sklearn import SKLearn
import numpy as np

# Konfigurasi sesi SageMaker dengan wilayah ap-southeast-3
boto_session = boto3.Session(region_name='ap-southeast-3')
sagemaker_session = sagemaker.Session(boto_session=boto_session)

# Tentukan path output di S3
bucket = 'your-s3-bucket'  # Ganti dengan nama bucket Anda
output_path = f's3://{bucket}/output'

# Buat estimator SKLearn untuk pelatihan lokal
sklearn_estimator = SKLearn(
    entry_point='train.py',
    role='arn:aws:iam::your-account-id:role/SageMakerRole',  # Ganti dengan ARN role Anda
    instance_type='local',
    framework_version='0.23-1',
    py_version='py3',
    output_path=output_path,
    sagemaker_session=sagemaker_session
)

# Latih model secara lokal
sklearn_estimator.fit({'train': 'file://./data/train.csv'})

# Deploy ke cloud
predictor = sklearn_estimator.deploy(initial_instance_count=1, instance_type='ml.m5.large')

# Uji model
data = np.array([[1.0, 2.0, 3.0]])  # Ganti dengan data input Anda
result = predictor.predict(data)
print(result)