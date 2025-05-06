import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export interface S3Props extends cdk.StackProps {
    bucketName?: string;
}

export class S3Resources extends Construct {
    public readonly bucket: s3.Bucket;

    constructor(scope: Construct, id: string, props: S3Props = {}) {
        super(scope, id);

        // Create S3 bucket with DESTROY removal policy
        this.bucket = new s3.Bucket(this, 'ModelBucket', {
            bucketName: props.bucketName ?? `model-bucket-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true, // Ensures objects are deleted when bucket is destroyed
            versioned: false, // No versioning for simplicity
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL, // Enforce private access
        });
    }
}