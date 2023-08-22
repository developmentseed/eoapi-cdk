import { Stack, aws_s3 as s3, aws_s3_deployment as s3_deployment} from "aws-cdk-lib";
import { RemovalPolicy, CfnOutput } from "aws-cdk-lib";
import { PolicyStatement, ServicePrincipal, Effect } from "aws-cdk-lib/aws-iam";

import { Construct } from "constructs";


export class StacBrowser extends Construct {

    public bucket: s3.Bucket;
    public bucketDeployment: s3_deployment.BucketDeployment;

    constructor(scope: Construct, id: string, props: StacBrowserProps) {
        super(scope, id);

        this.bucket = new s3.Bucket(this, 'Bucket', {
            accessControl: s3.BucketAccessControl.PRIVATE,
            removalPolicy: RemovalPolicy.DESTROY,
            })

        this.bucket.addToResourcePolicy(new PolicyStatement({
                    sid: 'AllowCloudFrontServicePrincipal',
                    effect: Effect.ALLOW, 
                    actions: ['s3:GetObject'],
                    principals: [new ServicePrincipal('cloudfront.amazonaws.com')],
                    resources: [this.bucket.arnForObjects('*')],
                    conditions: {
                        'StringEquals': {
                            'aws:SourceArn': props.cloudFrontDistributionArn
                        }
                    }
                }));
        

        this.bucketDeployment = new s3_deployment.BucketDeployment(this, 'BucketDeployment', {
            destinationBucket: this.bucket,
            sources: [s3_deployment.Source.asset(props.stacBrowserDistPath)]
          });

        new CfnOutput(this, "bucket-name", {
        exportName: `${Stack.of(this).stackName}-bucket-name`,
        value: this.bucket.bucketName,
        });

    }
}

export interface StacBrowserProps {

    /**
     * Location of the directory in the local filesystem that contains the STAC browser compiled code.
     */    
    readonly stacBrowserDistPath: string;


    /**
     * The ARN of the cloudfront distribution that will be added to the bucket policy with read access.
     *
     * @default - No cloudfront distribution ARN. The bucket policy will not be modified.
     */    
    readonly cloudFrontDistributionArn?: string;
    
    /**
     * The name of the index document (e.g. "index.html") for the website. Enables static website
     * hosting for this bucket.
     *
     * @default - No index document.
     */
    readonly websiteIndexDocument?: string;

}
