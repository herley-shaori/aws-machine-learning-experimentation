from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_sagemaker as sagemaker,
)
import aws_cdk as cdk
from constructs import Construct

class DeployModelStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load tags from configuration
        with open("resource_configuration.json", "r") as config_file:
            import json
            config = json.load(config_file)
            tags = config.get("tags", {})
            for key, value in tags.items():
                cdk.Tags.of(self).add(key, value)

        # Create S3 bucket with removal policy
        bucket = s3.Bucket(self, "ModelDeploymentBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create ECR repository with removal policy
        repository = ecr.Repository(self, "ModelDeploymentRepo",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_images=True
        )
        repository.add_lifecycle_rule(max_image_count=1, description="Keep only the latest image")

        # Create IAM role for CodeBuild
        codebuild_role = iam.Role(self, "CodeBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com")
        )
        repository.grant_pull_push(codebuild_role)
        bucket.grant_read(codebuild_role)

        # Environment variables for CodeBuild
        environment_variables = {
            "AWS_REGION": codebuild.BuildEnvironmentVariable(value=cdk.Aws.REGION),
            "ECR_REPOSITORY_URI": codebuild.BuildEnvironmentVariable(value=repository.repository_uri),
            "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(value="my-image"),
            "IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
        }

        # Create CodeBuild project
        project = codebuild.Project(self, "ModelDeploymentCodeBuild",
            source=codebuild.Source.s3(
                bucket=bucket,
                path="code.zip"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True
            ),
            environment_variables=environment_variables,
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml")
        )

        # Create VPC with two public subnets in different AZs
        vpc = ec2.Vpc(self, "MyVpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # Create security group for SageMaker
        security_group = ec2.SecurityGroup(self, "SageMakerSG",
            vpc=vpc,
            description="Security group for SageMaker endpoint",
            allow_all_outbound=True,
            security_group_name="SageMakerEndpointSG"
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS traffic"
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic from VPC"
        )

        # Create IAM role for SageMaker
        sagemaker_role = iam.Role(self, "SageMakerRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com")
        )
        sagemaker_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))
        repository.grant_pull(sagemaker_role)
        bucket.grant_read(sagemaker_role)

        # Create SageMaker model with VPC configuration
        image_uri = "623127157773.dkr.ecr.ap-southeast-3.amazonaws.com/deploymodelstack-modeldeploymentrepo918bd692-rtnjfjhqbcn5:latest"
        model = sagemaker.CfnModel(self, "MyModel",
            execution_role_arn=sagemaker_role.role_arn,
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image=image_uri
            ),
            enable_network_isolation=False,
            vpc_config=sagemaker.CfnModel.VpcConfigProperty(
                security_group_ids=[security_group.security_group_id],
                subnets=[subnet.subnet_id for subnet in vpc.public_subnets]
            ),
        )

        # Create SageMaker endpoint configuration
        endpoint_config = sagemaker.CfnEndpointConfig(self, "MyEndpointConfig",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=model.attr_model_name,
                    variant_name="AllTraffic",
                    instance_type="ml.m5.large",
                    initial_instance_count=1
                )
            ]
        )

        # Create SageMaker endpoint
        endpoint = sagemaker.CfnEndpoint(self, "MyEndpoint",
            endpoint_name="MyModelEndpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name
        )

        # Outputs
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "ECRRepositoryURI", value=repository.repository_uri)
        cdk.CfnOutput(self, "CodeBuildProjectName", value=project.project_name)