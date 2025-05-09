import * as cdk from 'aws-cdk-lib';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';

export interface CodeBuildProps extends cdk.StackProps {
    bucket: s3.IBucket;
    ecrRepository: ecr.Repository;
    imageTag?: string;
}

export class CodeBuildResources extends Construct {
    public readonly project: codebuild.Project;

    constructor(scope: Construct, id: string, props: CodeBuildProps) {
        super(scope, id);

        const imageTag = props.imageTag || 'latest';

        // Create the CodeBuild project
        this.project = new codebuild.Project(this, 'BuildProject', {
            source: codebuild.Source.s3({
                bucket: props.bucket,
                path: 'model_creation.zip',
            }),
            buildSpec: codebuild.BuildSpec.fromSourceFilename('buildspec.yml'),
            environment: {
                buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged: true, // Required for Docker in CodeBuild
                environmentVariables: {
                    AWS_REGION: { value: cdk.Aws.REGION },
                    ECR_REPOSITORY_URI: { value: props.ecrRepository.repositoryUri },
                    IMAGE_REPO_NAME: { value: props.ecrRepository.repositoryName },
                    IMAGE_TAG: { value: imageTag },
                },
            },
        });

        // Export the CodeBuild project name as a CloudFormation output
        new cdk.CfnOutput(this, 'CodeBuildProjectName', {
            value: this.project.projectName,
            description: 'Name of the CodeBuild project',
            exportName: 'CodeBuildProjectName',
        });

        // Grant permissions for ECR operations
        const ecrPolicy = new iam.PolicyStatement({
            actions: [
                'ecr:GetDownloadUrlForLayer',
                'ecr:BatchGetImage',
                'ecr:BatchCheckLayerAvailability',
                'ecr:PutImage',
                'ecr:InitiateLayerUpload',
                'ecr:UploadLayerPart',
                'ecr:CompleteLayerUpload',
            ],
            resources: [props.ecrRepository.repositoryArn],
        });

        const ecrAuthPolicy = new iam.PolicyStatement({
            actions: ['ecr:GetAuthorizationToken'],
            resources: ['*'],
        });

        this.project.addToRolePolicy(ecrPolicy);
        this.project.addToRolePolicy(ecrAuthPolicy);

        // Grant read access to the S3 bucket for the source code
        props.bucket.grantRead(this.project);
    }
}