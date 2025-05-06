#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import { DeployExternalModelToSagemakerRealtimeEndpointStack } from '../lib/2_deploy_external_model_to_sagemaker_realtime_endpoint-stack';

const app = new cdk.App();
new DeployExternalModelToSagemakerRealtimeEndpointStack(app, 'DeployExternalModelToSagemakerRealtimeEndpoint', {
    description: 'Deploys a pre-trained Random Forest model to an AWS SageMaker real-time endpoint for scalable inference.',
});