import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3_assets from 'aws-cdk-lib/aws-s3-assets';
import * as path from 'path';
import { Construct } from 'constructs';
import { Network } from './network';
import { SageMakerResources } from './sagemaker';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC and public subnet
    const network = new Network(this, 'Network', {
      maxAzs: 2,
    });

    // Create IAM role for SageMaker
    const sageMakerRole = new iam.Role(this, 'SageMakerExecutionRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
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

    // Define scikit-learn image URI (verify for ap-southeast-3)
    const imageUri = '951798379941.dkr.ecr.ap-southeast-3.amazonaws.com/sagemaker-scikit-learn:1.2-1';

    // Get subnet and security group IDs
    const subnetIds = network.vpc.publicSubnets.map(subnet => subnet.subnetId);
    const securityGroupIds = [network.securityGroup.securityGroupId];

    // Create model asset
    const modelAsset = new s3_assets.Asset(this, 'ModelAsset', {
      path: path.join(__dirname, '../model.tar.gz'),
    });

    // Grant read access to the SageMaker role
    modelAsset.grantRead(sageMakerRole);

    // Create SageMaker resources
    const sageMakerResources = new SageMakerResources(this, 'SageMaker', {
      modelDataUrl: modelAsset.s3ObjectUrl,
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