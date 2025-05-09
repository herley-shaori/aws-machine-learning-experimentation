import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { SageMakerResources } from './sagemaker';
import { S3Resources } from './s3';
import { EcrResources } from './ecr';
import { CodeBuildResources } from './codebuild';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create S3 bucket for model
    const s3Resources = new S3Resources(this, 'S3', {
      bucketName: `model-bucket-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
    });

    // Create ECR repository for model container
    const ecrResources = new EcrResources(this, 'ECR', {
      repositoryName: this.node.tryGetContext('ecrRepositoryName') || `model-repository-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
    });

    // Retrieve context value for image tag
    const imageTag = this.node.tryGetContext('imageTag') || 'latest';

    // Create CodeBuild resources
    const codeBuildResources = new CodeBuildResources(this, 'CodeBuild', {
      bucket: s3Resources.bucket,
      ecrRepository: ecrResources.repository,
      imageTag,
    });
  }
}