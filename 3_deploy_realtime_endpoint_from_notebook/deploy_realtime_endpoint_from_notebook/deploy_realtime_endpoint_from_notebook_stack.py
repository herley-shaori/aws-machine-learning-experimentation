from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class DeployRealtimeEndpointFromNotebookStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for SageMaker Notebook
        notebook_role = iam.Role(
            self,
            "NotebookRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Create S3 bucket
        bucket = s3.Bucket(
            self,
            "SageMakerBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Add S3 permissions to the notebook role
        bucket.grant_read_write(notebook_role)

        # Output the IAM Role ARN
        CfnOutput(
            self,
            "NotebookRoleArn",
            value=notebook_role.role_arn,
            description="ARN of the SageMaker Notebook IAM Role"
        )

        # Output the S3 Bucket Name
        CfnOutput(
            self,
            "BucketName",
            value=bucket.bucket_name,
            description="Name of the S3 Bucket"
        )