import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Network } from './network';

export class DeployExternalModelToSagemakerRealtimeEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC and public subnet
    const network = new Network(this, 'Network', {
      maxAzs: 2,
    });
  }
}