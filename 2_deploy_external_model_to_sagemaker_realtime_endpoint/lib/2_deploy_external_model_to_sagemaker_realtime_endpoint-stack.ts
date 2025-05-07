import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { Network } from './network';
import { SageMakerResources } from './sagemaker';
import { S3Resources } from './s3';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create S3 bucket for model
    const s3Resources = new S3Resources(this, 'S3Resources', {
      bucketName: `model-bucket-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
    });

    // Create VPC and public subnet
    const network = new Network(this, 'Network', {
      maxAzs: 2,
    });

    // Create IAM role for SageMaker
    const sageMakerRole = new iam.Role(this, 'SageMakerExecutionRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
    });

    // Add permissions for CloudWatch, Logs, EC2, and S3
    sageMakerRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        'cloudwatch:PutMetricData',
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
        'ec2:Describe*',
        's3:GetObject',
        's3:ListBucket',
      ],
      resources: [
        '*', // For CloudWatch, Logs, EC2
        s3Resources.bucket.bucketArn,
        `${s3Resources.bucket.bucketArn}/*`, // For S3 model access
      ],
    }));

    // Define scikit-learn image URI (ap-southeast-3)
    const imageUri = '951798379941.dkr.ecr.ap-southeast-3.amazonaws.com/sagemaker-scikit-learn:1.2-1';

    // Construct model URI
    const modelDataUrl = `s3://${s3Resources.bucket.bucketName}/model.tar.gz`;

    // Get subnet and security group IDs
    const subnetIds = network.vpc.publicSubnets.map(subnet => subnet.subnetId);
    const securityGroupIds = [network.securityGroup.securityGroupId];

    // Create SageMaker resources
    const sageMakerResources = new SageMakerResources(this, 'SageMaker', {
      modelDataUrl,
      executionRole: sageMakerRole,
      imageUri,
      subnetIds,
      securityGroupIds,
    });

    // Output the endpoint name
    new cdk.CfnOutput(this, 'EndpointName', {
      value: sageMakerResources.endpoint.endpointName!,
      description: 'Name of the SageMaker endpoint',
    });
  }
}