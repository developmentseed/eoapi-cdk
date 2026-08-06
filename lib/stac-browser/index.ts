import { Size, Stack, aws_s3 as s3, aws_s3_deployment as s3_deployment} from "aws-cdk-lib";
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
                autoDeleteObjects: props.autoDeleteObjects,
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
            sources: [s3_deployment.Source.asset(buildPath)],
            memoryLimit: 1024,
            ephemeralStorageSize: Size.mebibytes(1024),
          });

        new CfnOutput(this, "bucket-name", {
        exportName: `${Stack.of(this).stackName}-bucket-name`,
        value: this.bucket.bucketName,
        });

    }

    /**
     * Extracts the major version number from a stac-browser git tag, e.g.
     * "v4.0.1" -> 4, "v5.0.0-rc.2" -> 5, "4.0.1" -> 4.
     * Returns null if the tag doesn't match a recognizable semver-ish pattern
     * (e.g. a branch name or commit SHA was passed instead of a version tag).
     */
    private static parseMajorVersion(tag: string): number | null {
        const match = tag.match(/^v?(\d+)\./);
        return match ? parseInt(match[1], 10) : null;
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

        // Build the app with catalogUrl.
        // See: https://github.com/radiantearth/stac-browser/discussions/751
        const majorVersion = StacBrowser.parseMajorVersion(props.githubRepoTag);

        console.log(`Building app with catalogUrl=${props.stacCatalogUrl} into ${cloneDirectory} (detected major version: ${majorVersion ?? 'unknown'})`)

        if (majorVersion !== null && majorVersion <= 3) {
            // v3.x: CLI flag passthrough
            const args = [`--catalogUrl="${props.stacCatalogUrl}"`];
            if (props.pathPrefix) {
                args.push(`--pathPrefix="${props.pathPrefix}"`);
            }
            execSync(`npm run build -- ${args.join(' ')}`, { cwd: cloneDirectory });
        } else {
            // v4.x and v5.x (and anything newer, by default assumption): SB_* env vars.
            execSync('npm run build', {
                cwd: cloneDirectory,
                env: {
                    ...process.env,
                    SB_catalogUrl: props.stacCatalogUrl,
                    ...(props.pathPrefix ? { SB_pathPrefix: props.pathPrefix } : {}),
                },
            });
        }

        return `${cloneDirectory}/dist`

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
     *
     * Note: config.js option names have changed across major versions (particularly
     * into v5, which removed/renamed several options). Make sure the config file you
     * provide matches the schema of the `githubRepoTag` version you're building.
     */
    readonly configFilePath?: string;

    /**
     * Tag of the radiant earth stac-browser repo to use to build the app.
     */
    readonly githubRepoTag: string;

    /**
     * Sub-path the app will be hosted under (e.g. "/stac-browser"), if not deployed at
     * the root of the domain.
     *
     * Passed as a `--pathPrefix` CLI flag for <=v3.x, or as the `SB_pathPrefix`
     * environment variable for >=v4.x.
     *
     * @default - No path prefix. The app is built assuming it is served from the domain root.
     */
    readonly pathPrefix?: string;

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
     * Whether to automatically delete all objects in the managed bucket before
     * bucket deletion. Useful for ephemeral stacks and test environments.
     *
     * Ignored when `bucketArn` is provided because imported buckets are not
     * managed by this construct.
     *
     * @default - false
     */
    readonly autoDeleteObjects?: boolean;

    /**
     * Location in the filesystem where to compile the browser code.
     *
     * @default - DEFAULT_CLONE_DIRECTORY
     */
    readonly cloneDirectory?: string;

}
