from aws_cdk import (
    Stack,
    aws_iam as iam,
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
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )

        # Add VPC-related permissions to the role
        notebook_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ec2:DescribeSubnets",
                    "ec2:DescribeSecurityGroups",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:CreateNetworkInterface",
                    "ec2:DeleteNetworkInterface",
                    "ec2:ModifyNetworkInterfaceAttribute"
                ],
                resources=["*"]
            )
        )

        # Output the IAM Role ARN
        CfnOutput(
            self,
            "NotebookRoleArn",
            value=notebook_role.role_arn,
            description="ARN of the SageMaker Notebook IAM Role"
        )