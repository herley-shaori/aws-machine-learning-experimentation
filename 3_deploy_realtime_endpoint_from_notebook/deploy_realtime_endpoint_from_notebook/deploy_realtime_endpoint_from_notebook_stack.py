from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_sagemaker as sagemaker,
    aws_iam as iam
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
            allow_all_outbound=True  # Allow all outbound traffic
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

        # Create SageMaker Notebook Instance
        notebook_instance = sagemaker.CfnNotebookInstance(
            self,
            "NotebookInstance",
            instance_type="ml.t3.medium",  # Cost-effective instance type
            role_arn=notebook_role.role_arn,
            subnet_id=self.public_subnet_1.subnet_id,
            security_group_ids=[security_group.security_group_id],
            notebook_instance_name="MyNotebookInstance",
            direct_internet_access="Enabled"  # Required for public subnet access
        )