import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { SageMakerResources } from './sagemaker';
import { S3Resources } from './s3';
import { EcrResources } from './ecr';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create S3 bucket for model
    const s3Resources = new S3Resources(this, 'S3Resources', {
      bucketName: `model-bucket-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
    });

    // Create ECR repository for model container
    const ecrResources = new EcrResources(this, 'EcrResources', {
      repositoryName: `model-repository-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
    });
  }
}