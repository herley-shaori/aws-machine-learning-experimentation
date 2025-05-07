import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { SageMakerResources } from './sagemaker';
import { S3Resources } from './s3';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create S3 bucket for model
    const s3Resources = new S3Resources(this, 'S3Resources', {
      bucketName: `model-bucket-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
    });

    // Create IAM role for SageMaker
    const sageMakerRole = new iam.Role(this, 'SageMakerExecutionRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
      description: 'Role for SageMaker to access S3 and other services',
    });

    // Add permissions for CloudWatch, Logs, and EC2
    sageMakerRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        'cloudwatch:PutMetricData',
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
        'ec2:Describe*',
      ],
      resources: ['*'],
    }));

    // Add S3 permissions for model access
    sageMakerRole.addToPolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject', 's3:ListBucket'],
      resources: [
        s3Resources.bucket.bucketArn,
        `${s3Resources.bucket.bucketArn}/*`,
      ],
    }));

    // Add bucket policy to allow SageMaker role access
    s3Resources.bucket.addToResourcePolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject', 's3:ListBucket'],
      resources: [
        s3Resources.bucket.bucketArn,
        `${s3Resources.bucket.bucketArn}/*`,
      ],
      principals: [new iam.ArnPrincipal(sageMakerRole.roleArn)],
    }));

    // Define scikit-learn image URI (ap-southeast-3)
    const imageUri = '951798379941.dkr.ecr.ap-southeast-3.amazonaws.com/sagemaker-scikit-learn:1.2-1';

    // Construct model URI
    const modelDataUrl = `s3://${s3Resources.bucket.bucketName}/model.tar.gz`;

    // Create SageMaker resources
    const sageMakerResources = new SageMakerResources(this, 'SageMaker', {
      modelDataUrl,
      executionRole: sageMakerRole,
      imageUri,
    });

    // Ensure SageMaker endpoint depends on bucket and role
    sageMakerResources.node.addDependency(s3Resources.bucket);
    sageMakerResources.node.addDependency(sageMakerRole);

    // Output the endpoint name
    new cdk.CfnOutput(this, 'EndpointName', {
      value: sageMakerResources.endpoint.endpointName!,
      description: 'Name of the SageMaker endpoint',
    });
  }
}