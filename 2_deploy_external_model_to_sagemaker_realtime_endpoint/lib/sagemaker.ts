import * as cdk from 'aws-cdk-lib';
import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export interface SageMakerProps extends cdk.StackProps {
    modelBucket: s3.Bucket;
    executionRole: iam.IRole;
    imageUri: string;
    subnetIds: string[];
    securityGroupIds: string[];
}

export class SageMakerResources extends Construct {
    public readonly endpoint: sagemaker.CfnEndpoint;

    constructor(scope: Construct, id: string, props: SageMakerProps) {
        super(scope, id);

        const modelDataUrl = `s3://${props.modelBucket.bucketName}/model.tar.gz`;

        // Define the SageMaker model
        const model = new sagemaker.CfnModel(this, 'RandomForestModel', {
            executionRoleArn: props.executionRole.roleArn,
            primaryContainer: {
                image: props.imageUri,
                modelDataUrl: modelDataUrl,
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