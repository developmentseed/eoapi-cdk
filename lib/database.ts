import {
  Stack,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { BootstrapPgStac, BootstrapPgStacProps } from "./bootstrap-pgstac";

/**
 * An RDS instance with pgSTAC installed. This is a wrapper around the
 * `rds.DatabaseInstance` higher-level construct making use
 * of the BootstrapPgStac construct.
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
      parameterGroup,
      ...props,
    });

    const bootstrap = new BootstrapPgStac(this, "bootstrap-pgstac-instance", {
      vpc: props.vpc,
      database: this.db,
      dbSecret: this.db.secret!,
      pgstacDbName: props.pgstacDbName,
      pgstacVersion: props.pgstacVersion,
      pgstacUsername: props.pgstacUsername,
      secretsPrefix: props.secretsPrefix,
    });

    this.pgstacSecret = bootstrap.secret;
  }
}

export interface PgStacDatabaseProps extends rds.DatabaseInstanceProps {
  readonly pgstacDbName?: BootstrapPgStacProps["pgstacDbName"];
  readonly pgstacVersion?: BootstrapPgStacProps["pgstacVersion"];
  readonly pgstacUsername?: BootstrapPgStacProps["pgstacUsername"];
  readonly secretsPrefix?: BootstrapPgStacProps["secretsPrefix"];
}
