from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ec2 as ec2,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class DeployRealtimeEndpointFromNotebookStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with public subnets
        vpc = ec2.Vpc(
            self,
            "SageMakerVPC",
            cidr="10.0.0.0/16",
            max_azs=2,  # Use 2 AZs for high availability
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ],
            nat_gateways=0  # Public subnets don't need NAT gateways
        )

        # Create security group
        security_group = ec2.SecurityGroup(
            self,
            "SageMakerSG",
            vpc=vpc,
            description="Security group for SageMaker training and endpoint",
            allow_all_outbound=True  # Allow all outbound traffic
        )

        # Inbound rule: Allow all traffic from VPC CIDR
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic from VPC"
        )

        # Inbound rule: Allow HTTPS (port 443) from the world
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from the world"
        )

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

        # Output the VPC ID
        CfnOutput(
            self,
            "VpcId",
            value=vpc.vpc_id,
            description="ID of the VPC"
        )

        # Output the Subnet IDs
        CfnOutput(
            self,
            "SubnetIds",
            value=",".join(vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnet_ids),
            description="Comma-separated list of public subnet IDs"
        )

        # Output the Security Group ID
        CfnOutput(
            self,
            "SecurityGroupId",
            value=security_group.security_group_id,
            description="ID of the Security Group"
        )