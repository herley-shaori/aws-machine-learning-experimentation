#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import { DeployExternalModelToSagemakerRealtimeEndpointStack } from '../lib/deploy_external_model_to_sagemaker_realtime_endpoint-stack';

// Create the CDK app
const app = new cdk.App();

// Define global tags for all resources in the stack
const globalTags = {
    Project: 'AppliedAnalytics',
    Environment: 'Production',
    Purpose: 'SageMakerEndpoint',
    Owner: 'AnalyticsTeam',
};

// Instantiate the stack
const stack = new DeployExternalModelToSagemakerRealtimeEndpointStack(app, 'DeployExternalModelToSagemakerRealtimeEndpoint', {
    description: 'Deploys a pre-trained Random Forest model to an AWS SageMaker real-time endpoint for scalable inference.',
});

// Apply tags to all resources in the stack
Object.entries(globalTags).forEach(([key, value]) => {
    cdk.Tags.of(stack).add(key, value);
});

app.synth();