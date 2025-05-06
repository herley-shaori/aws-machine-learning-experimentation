import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Network } from './network';
import { S3Resources } from './s3';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC and public subnet
    const network = new Network(this, 'Network', {
      maxAzs: 2,
    });

    // Create S3 bucket
    const s3Resources = new S3Resources(this, 'S3');
  }
}