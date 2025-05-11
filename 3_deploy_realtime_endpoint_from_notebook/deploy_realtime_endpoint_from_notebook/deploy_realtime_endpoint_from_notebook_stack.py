from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    aws_s3 as s3,
    RemovalPolicy,
    Fn  # Added import for Fn
)
from constructs import Construct

class DeployRealtimeEndpointFromNotebookStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ],
            nat_gateways=0
        )

        # Store the subnets
        self.public_subnet_1 = vpc.public_subnets[0]
        self.public_subnet_2 = vpc.public_subnets[1]

        # Create Security Group
        security_group = ec2.SecurityGroup(
            self,
            "NotebookSecurityGroup",
            vpc=vpc,
            description="Security group for SageMaker Notebook",
            allow_all_outbound=True
        )

        # Add inbound rule for HTTPS (browser access)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS access from anywhere"
        )

        # Create IAM role for SageMaker Notebook
        notebook_role = iam.Role(
            self,
            "NotebookRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Create S3 bucket with removal policy
        notebook_bucket = s3.Bucket(
            self,
            "NotebookBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        # Grant the notebook role access to the S3 bucket
        notebook_bucket.grant_read_write(notebook_role)

        # Create SageMaker Lifecycle Configuration to set default S3 bucket
        lifecycle_config = sagemaker.CfnNotebookInstanceLifecycleConfig(
            self,
            "NotebookLifecycleConfig",
            notebook_instance_lifecycle_config_name="SetDefaultS3Bucket",
            on_start=[
                sagemaker.CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty(
                    content=Fn.base64(
                        f"#!/bin/bash\n"
                        f"aws s3 sync /home/ec2-user/SageMaker/ s3://{notebook_bucket.bucket_name}/\n"
                        f"echo 'export SAGEMAKER_DEFAULT_S3_BUCKET={notebook_bucket.bucket_name}' >> /home/ec2-user/.bashrc"
                    )
                )
            ]
        )

        # Create SageMaker Notebook Instance
        notebook_instance = sagemaker.CfnNotebookInstance(
            self,
            "NotebookInstance",
            instance_type="ml.t3.2xlarge",
            role_arn=notebook_role.role_arn,
            subnet_id=self.public_subnet_1.subnet_id,
            security_group_ids=[security_group.security_group_id],
            notebook_instance_name="MyNotebookInstance",
            direct_internet_access="Enabled",
            lifecycle_config_name=lifecycle_config.notebook_instance_lifecycle_config_name
        )