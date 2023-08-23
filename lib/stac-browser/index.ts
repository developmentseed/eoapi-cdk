import { Stack, aws_s3 as s3, aws_s3_deployment as s3_deployment} from "aws-cdk-lib";
import { RemovalPolicy, CfnOutput } from "aws-cdk-lib";
import { PolicyStatement, ServicePrincipal, Effect } from "aws-cdk-lib/aws-iam";

import { Construct } from "constructs";
import { execSync } from "child_process";
import * as fs from 'fs';

export class StacBrowser extends Construct {

    public bucket: s3.Bucket;
    public bucketDeployment: s3_deployment.BucketDeployment;

    constructor(scope: Construct, id: string, props: StacBrowserProps) {
        super(scope, id);

        const buildPath = this.buildApp(props.stacCatalogUrl, props.githubRepoTag);

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
            sources: [s3_deployment.Source.asset(buildPath)]
          });

        new CfnOutput(this, "bucket-name", {
        exportName: `${Stack.of(this).stackName}-bucket-name`,
        value: this.bucket.bucketName,
        });

    }

    private buildApp(stacCatalogUrl: string, githubRepoTag: string): string {
            
        // Define where to clone and build
        const cloneDirectory = './stac-browser';
        const githubRepoUrl = 'https://github.com/radiantearth/stac-browser.git';

        // if `cloneDirectory` exists, delete it
        if (fs.existsSync(cloneDirectory)) {
            console.log(`${cloneDirectory} already exists, deleting...`)
            execSync(`rm -rf ${cloneDirectory}`);
        }

        // Clone the repo
        console.log(`Cloning ${githubRepoUrl} into ${cloneDirectory}`)
        execSync(`git clone ${githubRepoUrl} ${cloneDirectory}`);

        // Check out the desired version
        console.log(`Checking out version ${githubRepoTag}`)
        execSync(`git checkout tags/${githubRepoTag}`, { cwd: cloneDirectory });

        // Install the dependencies and build the application
        console.log(`Installing dependencies`)
        execSync('npm install', { cwd: cloneDirectory });

        // Build the app with catalogUrl
        console.log(`Building app with catalogUrl=${stacCatalogUrl} into ${cloneDirectory}`)
        execSync(`npm run build -- --catalogUrl=${stacCatalogUrl}`, { cwd: cloneDirectory });

        return './stac-browser/dist'

    }


}

export interface StacBrowserProps {

    /**
     * STAC catalog URL
     */    
    readonly stacCatalogUrl: string;

    /**
     * Tag of the radiant earth stac-browser repo to use to build the app.
     */
    readonly githubRepoTag: string;


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
