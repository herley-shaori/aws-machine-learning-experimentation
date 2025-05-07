import * as cdk from 'aws-cdk-lib';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';

export interface EcrProps extends cdk.StackProps {
    repositoryName?: string;
}

export class EcrResources extends Construct {
    public readonly repository: ecr.Repository;

    constructor(scope: Construct, id: string, props: EcrProps = {}) {
        super(scope, id);

        // Create ECR repository
        this.repository = new ecr.Repository(this, 'ModelRepository', {
            repositoryName: props.repositoryName ?? `model-repository-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            imageScanOnPush: true,
        });

        // Add lifecycle policy to keep only the latest image
        this.repository.addLifecycleRule({
            rulePriority: 1,
            description: 'Keep only the latest image',
            maxImageCount: 1,
        });

        // Export the repository URI as a CloudFormation output
        new cdk.CfnOutput(this, 'RepositoryUri', {
            value: this.repository.repositoryUri,
            description: 'URI of the ECR repository for the model',
            exportName: 'ModelRepositoryUri',
        });
    }
}