import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { SageMakerRealTimeEndpoint } from './sagemaker';
import { S3Resources } from './s3';
import { EcrResources } from './ecr';
import { CodeBuildResources } from './codebuild';
import { Network } from './network';

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

    // Create network resources
    const network = new Network(this, 'Network', {
      maxAzs: 2,
    });

    // Create IAM role for SageMaker
    const sagemakerRole = new iam.Role(this, 'SageMakerExecutionRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonEC2ContainerRegistryReadOnly'),
      ],
    });

    // Create SageMaker real-time endpoint
    const sagemakerEndpoint = new SageMakerRealTimeEndpoint(this, 'SageMakerEndpoint', {
      modelDataUrl: `s3://${s3Resources.bucket.bucketName}/model.tar.gz`,
      executionRole: sagemakerRole,
      imageUri: '623127157773.dkr.ecr.ap-southeast-3.amazonaws.com/model-repository-623127157773-ap-southeast-3:latest',
      vpc: network.vpc,
      securityGroup: network.securityGroup,
    });
  }
}