import {
  Stack,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { BootstrapPgStac, BootstrapPgStacProps } from "../bootstrapper";

const instanceSizes: Record<string, number> = require("./instance-memory.json");

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

    const defaultParameters = this.getParameters(
      props.instanceType?.toString() || "m5.large",
      props.parameters
    );
    const parameterGroup = new rds.ParameterGroup(this, "parameterGroup", {
      engine: props.engine,
      parameters: {
        shared_buffers: defaultParameters.sharedBuffers,
        effective_cache_size: defaultParameters.effectiveCacheSize,
        work_mem: defaultParameters.workMem,
        maintenance_work_mem: defaultParameters.maintenanceWorkMem,
        max_locks_per_transaction: defaultParameters.maxLocksPerTransaction,
        temp_buffers: defaultParameters.tempBuffers,
        seq_page_cost: defaultParameters.seqPageCost,
        random_page_cost: defaultParameters.randomPageCost,
        ...props.parameters,
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

  public getParameters(
    instanceType: string,
    parameters: PgStacDatabaseProps["parameters"]
  ): DatabaseParameters {
    // https://github.com/aws/aws-cli/issues/1279#issuecomment-909318236
    const memory_in_kb = instanceSizes[instanceType] * 1024;

    // It's only necessary to consider passed in parameters for any value that used to
    // derive subsequent values. Values that don't have dependencies will be overriden
    // when we unpack the passed-in user parameters
    const maxConnections = parameters?.maxConnections
      ? Number.parseInt(parameters.maxConnections)
      : // https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html#RDS_Limits.MaxConnections
        Math.min(Math.round((memory_in_kb * 1024) / 9531392), 5000);
    const sharedBuffers = parameters?.sharedBufers
      ? Number.parseInt(parameters.sharedBufers)
      : Math.round(0.25 * memory_in_kb);

    const effectiveCacheSize = Math.round(0.75 * memory_in_kb);
    const workMem = Math.floor(sharedBuffers / maxConnections);
    const maintenanceWorkMem = Math.round(0.25 * sharedBuffers);

    const tempBuffers = 128 * 1024;
    const seqPageCost = 1;
    const randomPageCost = 1.1;

    return {
      maxConnections: `${maxConnections}`,
      sharedBuffers: `${sharedBuffers / 8}`, // Represented in 8kb blocks
      effectiveCacheSize: `${effectiveCacheSize}`,
      workMem: `${workMem}`,
      maintenanceWorkMem: `${maintenanceWorkMem}`,
      maxLocksPerTransaction: "1024",
      tempBuffers: `${tempBuffers}`,
      seqPageCost: `${seqPageCost}`,
      randomPageCost: `${randomPageCost}`,
    };
  }
}

export interface PgStacDatabaseProps extends rds.DatabaseInstanceProps {
  readonly pgstacDbName?: BootstrapPgStacProps["pgstacDbName"];
  readonly pgstacVersion?: BootstrapPgStacProps["pgstacVersion"];
  readonly pgstacUsername?: BootstrapPgStacProps["pgstacUsername"];
  readonly secretsPrefix?: BootstrapPgStacProps["secretsPrefix"];
}

export interface DatabaseParameters {
  /**
   * @default - LEAST({DBInstanceClassMemory/9531392}, 5000)
   */
  readonly maxConnections: string;

  /**
   * Note: This value is measured in 8KB blocks.
   *
   * @default '{DBInstanceClassMemory/32768}' 25% of instance memory, ie `{(DBInstanceClassMemory/(1024*8)) * 0.25}`
   */
  readonly sharedBuffers: string;

  /**
   * @default - 75% of instance memory
   */
  readonly effectiveCacheSize: string;

  /**
   * @default - shared buffers divided by max connections
   */
  readonly workMem: string;

  /**
   * @default - 25% of shared buffers
   */
  readonly maintenanceWorkMem: string;

  /**
   * @default 1024
   */
  readonly maxLocksPerTransaction: string;

  /**
   * @default 131172 (128 * 1024)
   */
  readonly tempBuffers: string;

  /**
   * @default 1
   */
  readonly seqPageCost: string;

  /**
   * @default 1.1
   */
  readonly randomPageCost: string;
}
