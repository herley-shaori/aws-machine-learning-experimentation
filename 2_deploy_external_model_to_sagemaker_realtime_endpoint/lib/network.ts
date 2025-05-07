import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface NetworkProps extends cdk.StackProps {
    maxAzs?: number;
}

export class Network extends Construct {
    public readonly vpc: ec2.Vpc;
    public readonly securityGroup: ec2.SecurityGroup;

    constructor(scope: Construct, id: string, props: NetworkProps = {}) {
        super(scope, id);

        // Create a VPC with public subnets
        this.vpc = new ec2.Vpc(this, 'VPC', {
            maxAzs: props.maxAzs ?? 2,
            subnetConfiguration: [
                {
                    cidrMask: 24,
                    name: 'Public',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
            ],
            natGateways: 0,
        });

        // Create a security group for SageMaker endpoint
        this.securityGroup = new ec2.SecurityGroup(this, 'SageMakerEndpointSG', {
            vpc: this.vpc,
            description: 'Security group for SageMaker endpoint',
            allowAllOutbound: true,
        });

        // Allow HTTPS traffic from anywhere
        this.securityGroup.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(443),
            'Allow HTTPS from anywhere'
        );
    }
}