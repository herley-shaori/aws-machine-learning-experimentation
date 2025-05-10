import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
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

        # Create S3 bucket
        bucket = s3.Bucket(self, "ModelDeploymentBucket")

        # Create ECR repository
        repository = ecr.Repository(self, "ModelDeploymentRepo")
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
                path="model_creation.zip"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True  # Needed for Docker
            ),
            environment_variables=environment_variables,
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml")
        )

        # Outputs
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "ECRRepositoryURI", value=repository.repository_uri)
        cdk.CfnOutput(self, "CodeBuildProjectName", value=project.project_name)