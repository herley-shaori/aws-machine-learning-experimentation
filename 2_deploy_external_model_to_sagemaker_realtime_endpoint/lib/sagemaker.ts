import * as cdk from 'aws-cdk-lib';
import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface SageMakerProps extends cdk.StackProps {
    modelDataUrl: string;
    executionRole: iam.IRole;
    imageUri: string;
    subnetIds: string[];
    securityGroupIds: string[];
}

export class SageMakerResources extends Construct {
    public readonly endpoint: sagemaker.CfnEndpoint;

    constructor(scope: Construct, id: string, props: SageMakerProps) {
        super(scope, id);

        // Define the SageMaker model
        const model = new sagemaker.CfnModel(this, 'RandomForestModel', {
            executionRoleArn: props.executionRole.roleArn,
            primaryContainer: {
                image: props.imageUri,
                modelDataUrl: props.modelDataUrl,
            },
        });

        // Define the endpoint configuration
        const endpointConfig = new sagemaker.CfnEndpointConfig(this, 'EndpointConfig', {
            productionVariants: [{
                modelName: model.attrModelName,
                variantName: 'AllTraffic',
                initialInstanceCount: 1,
                instanceType: 'ml.m5.large',
            }],
            vpcConfig: {
                subnets: props.subnetIds,
                securityGroupIds: props.securityGroupIds,
            },
        });

        // Define the endpoint
        this.endpoint = new sagemaker.CfnEndpoint(this, 'Endpoint', {
            endpointConfigName: endpointConfig.attrEndpointConfigName,
            endpointName: 'random-forest-endpoint',
        });
    }
}