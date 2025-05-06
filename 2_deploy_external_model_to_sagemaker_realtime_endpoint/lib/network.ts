import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface NetworkProps extends cdk.StackProps {
    maxAzs?: number;
}

export class Network extends Construct {
    public readonly vpc: ec2.Vpc;

    constructor(scope: Construct, id: string, props: NetworkProps = {}) {
        super(scope, id);

        // Create a VPC with a single public subnet
        this.vpc = new ec2.Vpc(this, 'VPC', {
            maxAzs: props.maxAzs ?? 2, // Default to 2 AZs for high availability
            subnetConfiguration: [
                {
                    cidrMask: 24,
                    name: 'Public',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
            ],
            natGateways: 0, // No NAT gateways needed for public-only setup
        });
    }
}