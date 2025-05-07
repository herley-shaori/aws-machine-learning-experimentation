import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { Network } from './network';
import { S3Resources } from './s3';
import { SageMakerResources } from './sagemaker';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC and public subnet
    const network = new Network(this, 'Network', {
      maxAzs: 2,
    });

    // Create S3 bucket
    const s3Resources = new S3Resources(this, 'S3');

    // Create IAM role for SageMaker
    const sageMakerRole = new iam.Role(this, 'SageMakerExecutionRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
    });

    // Grant S3 access
    sageMakerRole.addToPolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject'],
      resources: [s3Resources.bucket.arnForObjects('*')],
    }));

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

    // Define scikit-learn image URI (verify for ap-southeast-3)
    const imageUri = '763104351884.dkr.ecr.ap-southeast-3.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3';

    // Get subnet and security group IDs
    const subnetIds = network.vpc.publicSubnets.map(subnet => subnet.subnetId);
    const securityGroupIds = [network.securityGroup.securityGroupId];

    // Create SageMaker resources
    const sageMakerResources = new SageMakerResources(this, 'SageMaker', {
      modelBucket: s3Resources.bucket,
      executionRole: sageMakerRole,
      imageUri: imageUri,
      subnetIds: subnetIds,
      securityGroupIds: securityGroupIds,
    });

    // Output the endpoint name
    new cdk.CfnOutput(this, 'EndpointName', {
      value: sageMakerResources.endpoint.endpointName!,
      description: 'Name of the SageMaker endpoint',
    });
  }
}