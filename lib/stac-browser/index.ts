import { Stack, aws_s3 as s3, aws_s3_deployment as s3_deployment} from "aws-cdk-lib";
import { RemovalPolicy, CfnOutput } from "aws-cdk-lib";
import { PolicyStatement, ServicePrincipal, Effect } from "aws-cdk-lib/aws-iam";

import { Construct } from "constructs";
import { execSync } from "child_process";
import * as fs from 'fs';

const DEFAULT_CLONE_DIRECTORY = './stac-browser';

export class StacBrowser extends Construct {

    public bucket: s3.IBucket;
    public bucketDeployment: s3_deployment.BucketDeployment;

    constructor(scope: Construct, id: string, props: StacBrowserProps) {
        super(scope, id);

        const buildPath = this.buildApp(props, props.cloneDirectory || DEFAULT_CLONE_DIRECTORY);

        // import a bucket from props.bucketArn if defined, otherwise create a new bucket
        if (props.bucketArn) {
            this.bucket = s3.Bucket.fromBucketArn(this, 'Bucket', props.bucketArn);
        } else {
            this.bucket = new s3.Bucket(this, 'Bucket', {
                accessControl: s3.BucketAccessControl.PRIVATE,
                removalPolicy: RemovalPolicy.DESTROY,
                websiteIndexDocument: props.websiteIndexDocument
            })
        }

        // if props.cloudFrontDistributionArn is defined and props.bucketArn is not defined, add a bucket policy to allow read access from the cloudfront distribution
        if (props.cloudFrontDistributionArn && !props.bucketArn) {
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
        }

        // add the compiled code to the bucket as a bucket deployment
        this.bucketDeployment = new s3_deployment.BucketDeployment(this, 'BucketDeployment', {
            destinationBucket: this.bucket,
            sources: [s3_deployment.Source.asset(buildPath)]
          });

        new CfnOutput(this, "bucket-name", {
        exportName: `${Stack.of(this).stackName}-bucket-name`,
        value: this.bucket.bucketName,
        });

    }

    private buildApp(props: StacBrowserProps, cloneDirectory: string): string {

        // Define where to clone and build
        const githubRepoUrl = 'https://github.com/radiantearth/stac-browser.git';


        // Maybe the repo already exists in cloneDirectory. Try checking out the desired version and if it fails, delete and reclone.
        try {
            console.log(`Checking if a valid cloned repo exists with version ${props.githubRepoTag}...`)
            execSync(`git checkout tags/${props.githubRepoTag}`, { cwd: cloneDirectory });
        }
        catch (error) {

            // if directory exists, raise an error
            if (fs.existsSync(cloneDirectory)) {
                throw new Error(`Directory ${cloneDirectory} already exists and is not a valid clone of ${githubRepoUrl}. Please delete this directory or specify a different cloneDirectory.`);
            }

            // else, we clone and check out the version.

            // Clone the repo
            console.log(`Cloning ${githubRepoUrl} into ${cloneDirectory}...`)
            execSync(`git clone ${githubRepoUrl} ${cloneDirectory}`);

            // Check out the desired version
            console.log(`Checking out version ${props.githubRepoTag}...`)
            execSync(`git checkout tags/${props.githubRepoTag}`, { cwd: cloneDirectory });

        }

        // Install the dependencies and build the application
        console.log(`Installing dependencies`)
        execSync('npm install', { cwd: cloneDirectory });

        // If a config file is provided, copy it to the stac-browser directory at "config.js", replaces the default config.js.
        if (props.configFilePath) {
            // check that the file exists at this location. if not, raise an error and print current working directory.
            if (!fs.existsSync(props.configFilePath)) {
                throw new Error(`Config file ${props.configFilePath} does not exist. Current working directory is ${process.cwd()}`);
            }
            console.log(`Copying config file ${props.configFilePath} to ${cloneDirectory}/config.js`)
            fs.copyFileSync(props.configFilePath, `${cloneDirectory}/config.js`);
        }

        // Build the app with catalogUrl
        console.log(`Building app with catalogUrl=${props.stacCatalogUrl} into ${cloneDirectory}`)
        execSync(`npm run build -- --catalogUrl=${props.stacCatalogUrl}`, { cwd: cloneDirectory });

        return './stac-browser/dist'

    }


}

export interface StacBrowserProps {

    /**
     * Bucket ARN. If specified, the identity used to deploy the stack must have the appropriate permissions to create a deployment for this bucket.
     * In addition, if specified, `cloudFrontDistributionArn` is ignored since the policy of an imported resource can't be modified.
     *
     * @default - No bucket ARN. A new bucket will be created.
     */

    readonly bucketArn?: string;

    /**
     * STAC catalog URL. Overrides the catalog URL in the stac-browser configuration.
     */
    readonly stacCatalogUrl: string;

    /**
     * Path to config file for the STAC browser. If not provided, default configuration in the STAC browser
     * repository is used.
     */
    readonly configFilePath?: string;

    /**
     * Tag of the radiant earth stac-browser repo to use to build the app.
     */
    readonly githubRepoTag: string;


    /**
     * The ARN of the cloudfront distribution that will be added to the bucket policy with read access.
     * If `bucketArn` is specified, this parameter is ignored since the policy of an imported bucket can't be modified.
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

    /**
     * Location in the filesystem where to compile the browser code.
     *
     * @default - DEFAULT_CLONE_DIRECTORY
     */
    readonly cloneDirectory?: string;

}
