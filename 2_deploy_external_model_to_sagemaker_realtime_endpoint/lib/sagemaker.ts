import * as cdk from 'aws-cdk-lib';
import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import { Construct } from 'constructs';

export interface SageMakerRealTimeEndpointProps extends cdk.StackProps {
    modelDataUrl: string;
    executionRole: iam.IRole;
    imageUri: string;
    vpc: ec2.IVpc;
    securityGroup: ec2.ISecurityGroup;
}

export class SageMakerRealTimeEndpoint extends Construct {
    public readonly endpoint: sagemaker.CfnEndpoint;

    constructor(scope: Construct, id: string, props: SageMakerRealTimeEndpointProps) {
        super(scope, id);

        // Define the SageMaker model with vpcConfig
        const model = new sagemaker.CfnModel(this, 'Model', {
            executionRoleArn: props.executionRole.roleArn,
            primaryContainer: {
                image: props.imageUri,
                modelDataUrl: props.modelDataUrl,
            },
            vpcConfig: {
                subnets: props.vpc.publicSubnets.map(subnet => subnet.subnetId),
                securityGroupIds: [props.securityGroup.securityGroupId],
            },
        });

        // Define the endpoint configuration
        const endpointConfig = new sagemaker.CfnEndpointConfig(this, 'EndpointConfig', {
            productionVariants: [
                {
                    modelName: model.attrModelName,
                    variantName: 'AllTraffic',
                    initialInstanceCount: 1,
                    instanceType: 'ml.m5.large',
                },
            ],
        });

        // Define the endpoint
        this.endpoint = new sagemaker.CfnEndpoint(this, 'Endpoint', {
            endpointConfigName: endpointConfig.attrEndpointConfigName,
            endpointName: 'my-sagemaker-endpoint',
        });

        // Create CloudWatch Dashboard
        const dashboard = new cloudwatch.Dashboard(this, 'SageMakerDashboard', {
            dashboardName: 'SageMaker-Endpoint-Dashboard',
        });

        // Define CloudWatch metrics for the SageMaker endpoint
        const namespace = 'AWS/SageMaker';
        const dimensionsMap: cloudwatch.DimensionsMap = {
            EndpointName: this.endpoint.endpointName ?? 'my-sagemaker-endpoint',
            VariantName: 'AllTraffic',
        };

        const invocationsMetric = new cloudwatch.Metric({
            namespace,
            metricName: 'Invocations',
            dimensionsMap,
            statistic: 'Sum',
            period: cdk.Duration.minutes(5),
        });

        const modelLatencyMetric = new cloudwatch.Metric({
            namespace,
            metricName: 'ModelLatency',
            dimensionsMap,
            statistic: 'Average',
            period: cdk.Duration.minutes(5),
            unit: cloudwatch.Unit.MICROSECONDS,
        });

        const overheadLatencyMetric = new cloudwatch.Metric({
            namespace,
            metricName: 'OverheadLatency',
            dimensionsMap,
            statistic: 'Average',
            period: cdk.Duration.minutes(5),
            unit: cloudwatch.Unit.MICROSECONDS,
        });

        const invocationsPerInstanceMetric = new cloudwatch.Metric({
            namespace,
            metricName: 'InvocationsPerInstance',
            dimensionsMap,
            statistic: 'Average',
            period: cdk.Duration.minutes(5),
        });

        // Add widgets to the dashboard
        dashboard.addWidgets(
            new cloudwatch.GraphWidget({
                title: 'Endpoint Invocations',
                left: [invocationsMetric],
                width: 12,
            }),
            new cloudwatch.GraphWidget({
                title: 'Model Latency (ms)',
                left: [modelLatencyMetric.with({ unit: cloudwatch.Unit.MILLISECONDS })],
                width: 12,
            }),
            new cloudwatch.GraphWidget({
                title: 'Overhead Latency (ms)',
                left: [overheadLatencyMetric.with({ unit: cloudwatch.Unit.MILLISECONDS })],
                width: 12,
            }),
            new cloudwatch.GraphWidget({
                title: 'Invocations Per Instance',
                left: [invocationsPerInstanceMetric],
                width: 12,
            })
        );

        // Create CloudWatch Alarm for high model latency (>500ms)
        new cloudwatch.Alarm(this, 'HighModelLatencyAlarm', {
            alarmName: 'SageMaker-HighModelLatency',
            metric: modelLatencyMetric,
            threshold: 500000, // 500ms in microseconds
            evaluationPeriods: 2,
            comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarmDescription: 'Alarm when model latency exceeds 500ms',
            // Alarms are automatically deleted with the stack
        });

        // Create CloudWatch Alarm for invocation 5XX errors
        const invocation5xxErrorsMetric = new cloudwatch.Metric({
            namespace,
            metricName: 'Invocations5XXErrors',
            dimensionsMap,
            statistic: 'Sum',
            period: cdk.Duration.minutes(5),
        });

        new cloudwatch.Alarm(this, 'Invocation5xxErrorsAlarm', {
            alarmName: 'SageMaker-Invocation5xxErrors',
            metric: invocation5xxErrorsMetric,
            threshold: 1, // Alarm on any 5XX errors
            evaluationPeriods: 1,
            comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarmDescription: 'Alarm when invocation 5XX errors occur',
            // Alarms are automatically deleted with the stack
        });
    }
}