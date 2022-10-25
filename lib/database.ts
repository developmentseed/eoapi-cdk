import {
  Stack,
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { BootstrapPgStac } from "./bootstrap-pgstac";

/**
 * An RDS instance with pgSTAC installed.
 *
 * Will default to installing a `t3.small` Postgres instance.
 */
export class PgStacDatabase extends Construct {
  db: rds.DatabaseInstance;
  pgstacSecret: secretsmanager.ISecret;

  constructor(scope: Construct, id: string, props: PgStacDatabaseProps) {
    super(scope, id);

    const parameterGroup = new rds.ParameterGroup(this, "parameterGroup", {
      engine: props.engine,
      parameters: {
        max_locks_per_transaction: "1024",
        work_mem: "64000",
        temp_buffers: "32000",
      },
    });

    this.db = new rds.DatabaseInstance(this, "db", {
      instanceIdentifier: Stack.of(this).stackName,
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE3,
        ec2.InstanceSize.SMALL
      ),
      parameterGroup,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      ...props,
    });

    const bootstrap = new BootstrapPgStac(this, "bootstrap-pgstac-instance", {
      vpc: props.vpc,
      database: this.db,
      dbSecret: this.db.secret!,
      pgstacDbName: "pgstac",
      pgstacVersion: "0.6.8",
      pgstacUsername: "pgstac_user",
      secretsPrefix: "pgstac",
    });

    this.pgstacSecret = bootstrap.secret;
  }
}

export interface PgStacDatabaseProps extends rds.DatabaseInstanceProps {}
