# sagemaker_dev/deploy.py

import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel

# 1) Initialize session
boto_sess      = boto3.Session(region_name='ap-southeast-3')
sm_sess        = sagemaker.Session(boto_session=boto_sess)

# 2) Configuration
role           = 'arn:aws:iam::623127157773:role/DeployRealtimeEndpointFromNote-NotebookRoleCDEC1E3A-87HCGqVQrP0t'
bucket         = 'sagemaker-ap-southeast-3-623127157773'
training_job   = 'sagemaker-scikit-learn-2025-05-13-23-50-49-664'
model_artifact = f's3://{bucket}/output/{training_job}/output/model.tar.gz'

# 3) Create a SageMaker SKLearnModel pointing at inference.py
sk_model = SKLearnModel(
    model_data=model_artifact,
    role=role,
    entry_point='inference.py',      # <-- inference script
    source_dir='entrypoint',         # contains inference.py
    framework_version='0.23-1',
    py_version='py3',
    sagemaker_session=sm_sess
)

# 4) Deploy to an endpoint
predictor = sk_model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.2xlarge',
    endpoint_name='sklearn-linear-regression-endpoint-sm2',
    container_startup_health_check_timeout=300
)

print(f"Model deployed at endpoint: {predictor.endpoint_name}")
