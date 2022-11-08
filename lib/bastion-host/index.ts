import {
  Stack,
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_rds as rds,
  CfnOutput,
} from "aws-cdk-lib";
import { Construct } from "constructs";

/**
 * The database is located in an isolated subnet, meaning that it is not accessible from the public internet. As such, to interact with the database directly, a user must tunnel through a bastion host.
 *
 * ### Configuring
 *
 * This codebase controls _who_ is allowed to connect to the bastion host. This requires two steps:
 *
 * 1. Adding the IP address from which you are connecting to the `ipv4Allowlist` array
 * 1. Creating a bastion host system user by adding the user's configuration inform to `userdata.yaml`
 *
 * #### Adding an IP address to the `ipv4Allowlist` array
 *
 * The `BastionHost` construct takes in an `ipv4Allowlist` array as an argument. Find your IP address (eg `curl api.ipify.org`) and add that to the array along with the trailing CIDR block (likely `/32` to indicate that you are adding a single IP address).
 *
 * #### Creating a user via `userdata.yaml`
 *
 * Add an entry to the `users` array with a username (likely matching your local systems username, which you can get by running the `whoami` command in your terminal) and a public key (likely your default public key, which you can get by running `cat ~/.ssh/id_*.pub` in your terminal).
 *
 * #### Tips & Tricks when using the Bastion Host
 *
 * **Connecting to RDS Instance via SSM**
 *
 * ```sh
 * aws ssm start-session --target $INSTANCE_ID \
 * --document-name AWS-StartPortForwardingSessionToRemoteHost \
 * --parameters '{
 * "host": [
 * "example-db.c5abcdefghij.us-west-2.rds.amazonaws.com"
 * ],
 * "portNumber": [
 * "5432"
 * ],
 * "localPortNumber": [
 * "9999"
 * ]
 * }' \
 * --profile $AWS_PROFILE
 * ```
 *
 * ```sh
 * psql -h localhost -p 9999 # continue adding username (-U) and db (-d) here...
 * ```
 *
 * Connect directly to Bastion Host:
 *
 * ```sh
 * aws ssm start-session --target $INSTANCE_ID --profile $AWS_PROFILE
 * ```
 *
 * **Setting up an SSH tunnel**
 *
 * In your `~/.ssh/config` file, add an entry like:
 *
 * ```
 * Host db-tunnel
 * Hostname {the-bastion-host-address}
 * LocalForward 54322 {the-db-hostname}:5432
 * ```
 *
 * Then a tunnel can be opened via:
 *
 * ```
 * ssh -N db-tunnel
 * ```
 *
 * And a connection to the DB can be made via:
 *
 * ```
 * psql -h 127.0.0.1 -p 5433 -U {username} -d {database}
 * ```
 *
 * **Handling `REMOTE HOST IDENTIFICATION HAS CHANGED!` error**
 *
 * If you've redeployed a bastion host that you've previously connected to, you may see an error like:
 *
 * ```
 * @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 * @    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
 * @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 * IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
 * Someone could be eavesdropping on you right now (man-in-the-middle attack)!
 * It is also possible that a host key has just been changed.
 * The fingerprint for the ECDSA key sent by the remote host is
 * SHA256:mPnxAOXTpb06PFgI1Qc8TMQ2e9b7goU8y2NdS5hzIr8.
 * Please contact your system administrator.
 * Add correct host key in /Users/username/.ssh/known_hosts to get rid of this message.
 * Offending ECDSA key in /Users/username/.ssh/known_hosts:28
 * ECDSA host key for ec2-12-34-56-789.us-west-2.compute.amazonaws.com has changed and you have requested strict checking.
 * Host key verification failed.
 * ```
 *
 * This is due to the server's fingerprint changing. We can scrub the fingerprint from our system with a command like:
 *
 * ```
 * ssh-keygen -R 12.34.56.789
 * ```
 *
 */
export class BastionHost extends Construct {
  instance: ec2.Instance;

  constructor(scope: Construct, id: string, props: BastionHostProps) {
    super(scope, id);

    const { stackName } = Stack.of(this);

    // Build ec2 instance
    this.instance = new ec2.Instance(this, "bastion-host", {
      vpc: props.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      instanceName: `${stackName} bastion host`,
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE4_GRAVITON,
        ec2.InstanceSize.NANO
      ),
      machineImage: ec2.MachineImage.latestAmazonLinux({
        generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        cpuType: ec2.AmazonLinuxCpuType.ARM_64,
      }),
      userData: props.userData,
      userDataCausesReplacement: true,
    });

    // Assign elastic IP
    if (props.createElasticIp ?? true) {
      new ec2.CfnEIP(this, "IP", {
        instanceId: this.instance.instanceId,
        tags: [{ key: "Name", value: stackName }],
      });
    }

    // Allow bastion host to connect to db
    this.instance.connections.allowTo(
      props.db.connections.securityGroups[0],
      ec2.Port.tcp(5432),
      "Allow connection from bastion host"
    );

    // Allow IP access to bastion host
    for (const ipv4 of props.ipv4Allowlist) {
      this.instance.connections.allowFrom(
        ec2.Peer.ipv4(ipv4),
        ec2.Port.tcp(props.sshPort || 22),
        "SSH Access"
      );
    }

    // Integrate with SSM
    this.instance.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "ssmmessages:*",
          "ssm:UpdateInstanceInformation",
          "ec2messages:*",
        ],
        resources: ["*"],
      })
    );

    new CfnOutput(this, "instance-id-output", {
      value: this.instance.instanceId,
      exportName: `${stackName}-instance-id`,
    });
    new CfnOutput(this, "instance-public-ip-output", {
      value: this.instance.instancePublicIp,
      exportName: `${stackName}-instance-public-ip`,
    });
    new CfnOutput(this, "instance-public-dns-name-output", {
      value: this.instance.instancePublicDnsName,
      exportName: `${stackName}-public-dns-name`,
    });
  }
}

export interface BastionHostProps {
  readonly vpc: ec2.IVpc;
  readonly db: rds.IDatabaseInstance;
  readonly userData: ec2.UserData;
  readonly ipv4Allowlist: string[];
  readonly sshPort?: number;

  /**
   * Whether or not an elastic IP should be created for the bastion host.
   *
   * @default false
   */
  readonly createElasticIp?: boolean;
}
