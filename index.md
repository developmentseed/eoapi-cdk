# API Reference <a name="API Reference" id="api-reference"></a>

## Constructs <a name="Constructs" id="Constructs"></a>

### BootstrapPgStac <a name="BootstrapPgStac" id="pgstac-cdk-construct.BootstrapPgStac"></a>

Bootstraps a database instance, installing pgSTAC onto the database.

#### Initializers <a name="Initializers" id="pgstac-cdk-construct.BootstrapPgStac.Initializer"></a>

```typescript
import { BootstrapPgStac } from 'pgstac-cdk-construct'

new BootstrapPgStac(scope: Construct, id: string, props: BootstrapPgStacProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.Initializer.parameter.props">props</a></code> | <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps">BootstrapPgStacProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="pgstac-cdk-construct.BootstrapPgStac.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="pgstac-cdk-construct.BootstrapPgStac.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="pgstac-cdk-construct.BootstrapPgStac.Initializer.parameter.props"></a>

- *Type:* <a href="#pgstac-cdk-construct.BootstrapPgStacProps">BootstrapPgStacProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="pgstac-cdk-construct.BootstrapPgStac.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="pgstac-cdk-construct.BootstrapPgStac.isConstruct"></a>

```typescript
import { BootstrapPgStac } from 'pgstac-cdk-construct'

BootstrapPgStac.isConstruct(x: any)
```

Checks if `x` is a construct.

Use this method instead of `instanceof` to properly detect `Construct`
instances, even when the construct library is symlinked.

Explanation: in JavaScript, multiple copies of the `constructs` library on
disk are seen as independent, completely different libraries. As a
consequence, the class `Construct` in each copy of the `constructs` library
is seen as a different class, and an instance of one class will not test as
`instanceof` the other class. `npm install` will not create installations
like this, but users may manually symlink construct libraries together or
use a monorepo tool: in those cases, multiple copies of the `constructs`
library can be accidentally installed, and `instanceof` will behave
unpredictably. It is safest to avoid using `instanceof`, and using
this type-testing method instead.

###### `x`<sup>Required</sup> <a name="x" id="pgstac-cdk-construct.BootstrapPgStac.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStac.property.secret">secret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="pgstac-cdk-construct.BootstrapPgStac.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `secret`<sup>Required</sup> <a name="secret" id="pgstac-cdk-construct.BootstrapPgStac.property.secret"></a>

```typescript
public readonly secret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

---


### PgStacDatabase <a name="PgStacDatabase" id="pgstac-cdk-construct.PgStacDatabase"></a>

An RDS instance with pgSTAC installed.

Will default to installing a `t3.small` Postgres instance.

#### Initializers <a name="Initializers" id="pgstac-cdk-construct.PgStacDatabase.Initializer"></a>

```typescript
import { PgStacDatabase } from 'pgstac-cdk-construct'

new PgStacDatabase(scope: Construct, id: string, props: Props)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.Initializer.parameter.props">props</a></code> | <code><a href="#pgstac-cdk-construct.Props">Props</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="pgstac-cdk-construct.PgStacDatabase.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="pgstac-cdk-construct.PgStacDatabase.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="pgstac-cdk-construct.PgStacDatabase.Initializer.parameter.props"></a>

- *Type:* <a href="#pgstac-cdk-construct.Props">Props</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="pgstac-cdk-construct.PgStacDatabase.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="pgstac-cdk-construct.PgStacDatabase.isConstruct"></a>

```typescript
import { PgStacDatabase } from 'pgstac-cdk-construct'

PgStacDatabase.isConstruct(x: any)
```

Checks if `x` is a construct.

Use this method instead of `instanceof` to properly detect `Construct`
instances, even when the construct library is symlinked.

Explanation: in JavaScript, multiple copies of the `constructs` library on
disk are seen as independent, completely different libraries. As a
consequence, the class `Construct` in each copy of the `constructs` library
is seen as a different class, and an instance of one class will not test as
`instanceof` the other class. `npm install` will not create installations
like this, but users may manually symlink construct libraries together or
use a monorepo tool: in those cases, multiple copies of the `constructs`
library can be accidentally installed, and `instanceof` will behave
unpredictably. It is safest to avoid using `instanceof`, and using
this type-testing method instead.

###### `x`<sup>Required</sup> <a name="x" id="pgstac-cdk-construct.PgStacDatabase.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.DatabaseInstance</code> | *No description.* |
| <code><a href="#pgstac-cdk-construct.PgStacDatabase.property.pgstacSecret">pgstacSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="pgstac-cdk-construct.PgStacDatabase.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `db`<sup>Required</sup> <a name="db" id="pgstac-cdk-construct.PgStacDatabase.property.db"></a>

```typescript
public readonly db: DatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.DatabaseInstance

---

##### `pgstacSecret`<sup>Required</sup> <a name="pgstacSecret" id="pgstac-cdk-construct.PgStacDatabase.property.pgstacSecret"></a>

```typescript
public readonly pgstacSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

---


## Structs <a name="Structs" id="Structs"></a>

### BootstrapPgStacProps <a name="BootstrapPgStacProps" id="pgstac-cdk-construct.BootstrapPgStacProps"></a>

#### Initializer <a name="Initializer" id="pgstac-cdk-construct.BootstrapPgStacProps.Initializer"></a>

```typescript
import { BootstrapPgStacProps } from 'pgstac-cdk-construct'

const bootstrapPgStacProps: BootstrapPgStacProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.database">database</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance \| aws-cdk-lib.aws_rds.DatabaseInstance</code> | Database onto which pgSTAC should be installed. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing valid connection details for the database instance. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.pgstacVersion">pgstacVersion</a></code> | <code>string</code> | pgSTAC version to be installed. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.schemaVersion">schemaVersion</a></code> | <code>string</code> | A nonce value to be used for triggering re-runs of migrations. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.secretsPrefix">secretsPrefix</a></code> | <code>string</code> | Prefix to assign to the generated `secrets_manager.Secret`. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.pgstacDbName">pgstacDbName</a></code> | <code>string</code> | Name of database that is to be created and onto which pgSTAC will be installed. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.pgstacUsername">pgstacUsername</a></code> | <code>string</code> | Name of user that will be generated for connecting to the pgSTAC database. |
| <code><a href="#pgstac-cdk-construct.BootstrapPgStacProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC in which the database resides. |

---

##### `database`<sup>Required</sup> <a name="database" id="pgstac-cdk-construct.BootstrapPgStacProps.property.database"></a>

```typescript
public readonly database: IDatabaseInstance | DatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance | aws-cdk-lib.aws_rds.DatabaseInstance

Database onto which pgSTAC should be installed.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="pgstac-cdk-construct.BootstrapPgStacProps.property.dbSecret"></a>

```typescript
public readonly dbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing valid connection details for the database instance.

Secret must
conform to the format of CDK's `DatabaseInstance` (i.e. a JSON object containing a
`username`, `password`, `host`, `port`, and optionally a `dbname`). If a `dbname`
property is not specified within the secret, the bootstrapper will attempt to
connect to a database with the name of `"postgres"`.

---

##### `pgstacVersion`<sup>Required</sup> <a name="pgstacVersion" id="pgstac-cdk-construct.BootstrapPgStacProps.property.pgstacVersion"></a>

```typescript
public readonly pgstacVersion: string;
```

- *Type:* string

pgSTAC version to be installed.

---

##### `schemaVersion`<sup>Required</sup> <a name="schemaVersion" id="pgstac-cdk-construct.BootstrapPgStacProps.property.schemaVersion"></a>

```typescript
public readonly schemaVersion: string;
```

- *Type:* string

A nonce value to be used for triggering re-runs of migrations.

---

##### `secretsPrefix`<sup>Required</sup> <a name="secretsPrefix" id="pgstac-cdk-construct.BootstrapPgStacProps.property.secretsPrefix"></a>

```typescript
public readonly secretsPrefix: string;
```

- *Type:* string
- *Default:* "pgstac"

Prefix to assign to the generated `secrets_manager.Secret`.

---

##### `pgstacDbName`<sup>Optional</sup> <a name="pgstacDbName" id="pgstac-cdk-construct.BootstrapPgStacProps.property.pgstacDbName"></a>

```typescript
public readonly pgstacDbName: string;
```

- *Type:* string
- *Default:* "pgstac"

Name of database that is to be created and onto which pgSTAC will be installed.

---

##### `pgstacUsername`<sup>Optional</sup> <a name="pgstacUsername" id="pgstac-cdk-construct.BootstrapPgStacProps.property.pgstacUsername"></a>

```typescript
public readonly pgstacUsername: string;
```

- *Type:* string
- *Default:* "pgstac_user"

Name of user that will be generated for connecting to the pgSTAC database.

---

##### `vpc`<sup>Optional</sup> <a name="vpc" id="pgstac-cdk-construct.BootstrapPgStacProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc
- *Default:* `vpc` property of the `database` instance provided.

VPC in which the database resides.

Note - Must be explicitely set if the `database` only conforms to the
`aws_rds.IDatabaseInstace` interface (ie it is a reference to a database instance
rather than a database instance.)

---

### Props <a name="Props" id="pgstac-cdk-construct.Props"></a>

#### Initializer <a name="Initializer" id="pgstac-cdk-construct.Props.Initializer"></a>

```typescript
import { Props } from 'pgstac-cdk-construct'

const props: Props = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#pgstac-cdk-construct.Props.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | The VPC network where the DB subnet group should be created. |
| <code><a href="#pgstac-cdk-construct.Props.property.autoMinorVersionUpgrade">autoMinorVersionUpgrade</a></code> | <code>boolean</code> | Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. |
| <code><a href="#pgstac-cdk-construct.Props.property.availabilityZone">availabilityZone</a></code> | <code>string</code> | The name of the Availability Zone where the DB instance will be located. |
| <code><a href="#pgstac-cdk-construct.Props.property.backupRetention">backupRetention</a></code> | <code>aws-cdk-lib.Duration</code> | The number of days during which automatic DB snapshots are retained. |
| <code><a href="#pgstac-cdk-construct.Props.property.cloudwatchLogsExports">cloudwatchLogsExports</a></code> | <code>string[]</code> | The list of log types that need to be enabled for exporting to CloudWatch Logs. |
| <code><a href="#pgstac-cdk-construct.Props.property.cloudwatchLogsRetention">cloudwatchLogsRetention</a></code> | <code>aws-cdk-lib.aws_logs.RetentionDays</code> | The number of days log events are kept in CloudWatch Logs. |
| <code><a href="#pgstac-cdk-construct.Props.property.cloudwatchLogsRetentionRole">cloudwatchLogsRetentionRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | The IAM role for the Lambda function associated with the custom resource that sets the retention policy. |
| <code><a href="#pgstac-cdk-construct.Props.property.copyTagsToSnapshot">copyTagsToSnapshot</a></code> | <code>boolean</code> | Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.deleteAutomatedBackups">deleteAutomatedBackups</a></code> | <code>boolean</code> | Indicates whether automated backups should be deleted or retained when you delete a DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.deletionProtection">deletionProtection</a></code> | <code>boolean</code> | Indicates whether the DB instance should have deletion protection enabled. |
| <code><a href="#pgstac-cdk-construct.Props.property.domain">domain</a></code> | <code>string</code> | The Active Directory directory ID to create the DB instance in. |
| <code><a href="#pgstac-cdk-construct.Props.property.domainRole">domainRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | The IAM role to be used when making API calls to the Directory Service. |
| <code><a href="#pgstac-cdk-construct.Props.property.enablePerformanceInsights">enablePerformanceInsights</a></code> | <code>boolean</code> | Whether to enable Performance Insights for the DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.iamAuthentication">iamAuthentication</a></code> | <code>boolean</code> | Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. |
| <code><a href="#pgstac-cdk-construct.Props.property.instanceIdentifier">instanceIdentifier</a></code> | <code>string</code> | A name for the DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.iops">iops</a></code> | <code>number</code> | The number of I/O operations per second (IOPS) that the database provisions. |
| <code><a href="#pgstac-cdk-construct.Props.property.maxAllocatedStorage">maxAllocatedStorage</a></code> | <code>number</code> | Upper limit to which RDS can scale the storage in GiB(Gibibyte). |
| <code><a href="#pgstac-cdk-construct.Props.property.monitoringInterval">monitoringInterval</a></code> | <code>aws-cdk-lib.Duration</code> | The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.monitoringRole">monitoringRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be used to manage DB instance monitoring. |
| <code><a href="#pgstac-cdk-construct.Props.property.multiAz">multiAz</a></code> | <code>boolean</code> | Specifies if the database instance is a multiple Availability Zone deployment. |
| <code><a href="#pgstac-cdk-construct.Props.property.optionGroup">optionGroup</a></code> | <code>aws-cdk-lib.aws_rds.IOptionGroup</code> | The option group to associate with the instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.parameterGroup">parameterGroup</a></code> | <code>aws-cdk-lib.aws_rds.IParameterGroup</code> | The DB parameter group to associate with the instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.performanceInsightEncryptionKey">performanceInsightEncryptionKey</a></code> | <code>aws-cdk-lib.aws_kms.IKey</code> | The AWS KMS key for encryption of Performance Insights data. |
| <code><a href="#pgstac-cdk-construct.Props.property.performanceInsightRetention">performanceInsightRetention</a></code> | <code>aws-cdk-lib.aws_rds.PerformanceInsightRetention</code> | The amount of time, in days, to retain Performance Insights data. |
| <code><a href="#pgstac-cdk-construct.Props.property.port">port</a></code> | <code>number</code> | The port for the instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.preferredBackupWindow">preferredBackupWindow</a></code> | <code>string</code> | The daily time range during which automated backups are performed. |
| <code><a href="#pgstac-cdk-construct.Props.property.preferredMaintenanceWindow">preferredMaintenanceWindow</a></code> | <code>string</code> | The weekly time range (in UTC) during which system maintenance can occur. |
| <code><a href="#pgstac-cdk-construct.Props.property.processorFeatures">processorFeatures</a></code> | <code>aws-cdk-lib.aws_rds.ProcessorFeatures</code> | The number of CPU cores and the number of threads per core. |
| <code><a href="#pgstac-cdk-construct.Props.property.publiclyAccessible">publiclyAccessible</a></code> | <code>boolean</code> | Indicates whether the DB instance is an internet-facing instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.removalPolicy">removalPolicy</a></code> | <code>aws-cdk-lib.RemovalPolicy</code> | The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. |
| <code><a href="#pgstac-cdk-construct.Props.property.s3ExportBuckets">s3ExportBuckets</a></code> | <code>aws-cdk-lib.aws_s3.IBucket[]</code> | S3 buckets that you want to load data into. |
| <code><a href="#pgstac-cdk-construct.Props.property.s3ExportRole">s3ExportRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be associated with this DB instance to enable S3 export. |
| <code><a href="#pgstac-cdk-construct.Props.property.s3ImportBuckets">s3ImportBuckets</a></code> | <code>aws-cdk-lib.aws_s3.IBucket[]</code> | S3 buckets that you want to load data from. |
| <code><a href="#pgstac-cdk-construct.Props.property.s3ImportRole">s3ImportRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be associated with this DB instance to enable S3 import. |
| <code><a href="#pgstac-cdk-construct.Props.property.securityGroups">securityGroups</a></code> | <code>aws-cdk-lib.aws_ec2.ISecurityGroup[]</code> | The security groups to assign to the DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.storageType">storageType</a></code> | <code>aws-cdk-lib.aws_rds.StorageType</code> | The storage type. |
| <code><a href="#pgstac-cdk-construct.Props.property.subnetGroup">subnetGroup</a></code> | <code>aws-cdk-lib.aws_rds.ISubnetGroup</code> | Existing subnet group for the instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.vpcSubnets">vpcSubnets</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | The type of subnets to add to the created DB subnet group. |
| <code><a href="#pgstac-cdk-construct.Props.property.engine">engine</a></code> | <code>aws-cdk-lib.aws_rds.IInstanceEngine</code> | The database engine. |
| <code><a href="#pgstac-cdk-construct.Props.property.allocatedStorage">allocatedStorage</a></code> | <code>number</code> | The allocated storage size, specified in gibibytes (GiB). |
| <code><a href="#pgstac-cdk-construct.Props.property.allowMajorVersionUpgrade">allowMajorVersionUpgrade</a></code> | <code>boolean</code> | Whether to allow major version upgrades. |
| <code><a href="#pgstac-cdk-construct.Props.property.databaseName">databaseName</a></code> | <code>string</code> | The name of the database. |
| <code><a href="#pgstac-cdk-construct.Props.property.instanceType">instanceType</a></code> | <code>aws-cdk-lib.aws_ec2.InstanceType</code> | The name of the compute and memory capacity for the instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.licenseModel">licenseModel</a></code> | <code>aws-cdk-lib.aws_rds.LicenseModel</code> | The license model. |
| <code><a href="#pgstac-cdk-construct.Props.property.parameters">parameters</a></code> | <code>{[ key: string ]: string}</code> | The parameters in the DBParameterGroup to create automatically. |
| <code><a href="#pgstac-cdk-construct.Props.property.timezone">timezone</a></code> | <code>string</code> | The time zone of the instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.characterSetName">characterSetName</a></code> | <code>string</code> | For supported engines, specifies the character set to associate with the DB instance. |
| <code><a href="#pgstac-cdk-construct.Props.property.credentials">credentials</a></code> | <code>aws-cdk-lib.aws_rds.Credentials</code> | Credentials for the administrative user. |
| <code><a href="#pgstac-cdk-construct.Props.property.storageEncrypted">storageEncrypted</a></code> | <code>boolean</code> | Indicates whether the DB instance is encrypted. |
| <code><a href="#pgstac-cdk-construct.Props.property.storageEncryptionKey">storageEncryptionKey</a></code> | <code>aws-cdk-lib.aws_kms.IKey</code> | The KMS key that's used to encrypt the DB instance. |

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="pgstac-cdk-construct.Props.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

The VPC network where the DB subnet group should be created.

---

##### `autoMinorVersionUpgrade`<sup>Optional</sup> <a name="autoMinorVersionUpgrade" id="pgstac-cdk-construct.Props.property.autoMinorVersionUpgrade"></a>

```typescript
public readonly autoMinorVersionUpgrade: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window.

---

##### `availabilityZone`<sup>Optional</sup> <a name="availabilityZone" id="pgstac-cdk-construct.Props.property.availabilityZone"></a>

```typescript
public readonly availabilityZone: string;
```

- *Type:* string
- *Default:* no preference

The name of the Availability Zone where the DB instance will be located.

---

##### `backupRetention`<sup>Optional</sup> <a name="backupRetention" id="pgstac-cdk-construct.Props.property.backupRetention"></a>

```typescript
public readonly backupRetention: Duration;
```

- *Type:* aws-cdk-lib.Duration
- *Default:* Duration.days(1) for source instances, disabled for read replicas

The number of days during which automatic DB snapshots are retained.

Set to zero to disable backups.
When creating a read replica, you must enable automatic backups on the source
database instance by setting the backup retention to a value other than zero.

---

##### `cloudwatchLogsExports`<sup>Optional</sup> <a name="cloudwatchLogsExports" id="pgstac-cdk-construct.Props.property.cloudwatchLogsExports"></a>

```typescript
public readonly cloudwatchLogsExports: string[];
```

- *Type:* string[]
- *Default:* no log exports

The list of log types that need to be enabled for exporting to CloudWatch Logs.

---

##### `cloudwatchLogsRetention`<sup>Optional</sup> <a name="cloudwatchLogsRetention" id="pgstac-cdk-construct.Props.property.cloudwatchLogsRetention"></a>

```typescript
public readonly cloudwatchLogsRetention: RetentionDays;
```

- *Type:* aws-cdk-lib.aws_logs.RetentionDays
- *Default:* logs never expire

The number of days log events are kept in CloudWatch Logs.

When updating
this property, unsetting it doesn't remove the log retention policy. To
remove the retention policy, set the value to `Infinity`.

---

##### `cloudwatchLogsRetentionRole`<sup>Optional</sup> <a name="cloudwatchLogsRetentionRole" id="pgstac-cdk-construct.Props.property.cloudwatchLogsRetentionRole"></a>

```typescript
public readonly cloudwatchLogsRetentionRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* a new role is created.

The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

---

##### `copyTagsToSnapshot`<sup>Optional</sup> <a name="copyTagsToSnapshot" id="pgstac-cdk-construct.Props.property.copyTagsToSnapshot"></a>

```typescript
public readonly copyTagsToSnapshot: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance.

---

##### `deleteAutomatedBackups`<sup>Optional</sup> <a name="deleteAutomatedBackups" id="pgstac-cdk-construct.Props.property.deleteAutomatedBackups"></a>

```typescript
public readonly deleteAutomatedBackups: boolean;
```

- *Type:* boolean
- *Default:* false

Indicates whether automated backups should be deleted or retained when you delete a DB instance.

---

##### `deletionProtection`<sup>Optional</sup> <a name="deletionProtection" id="pgstac-cdk-construct.Props.property.deletionProtection"></a>

```typescript
public readonly deletionProtection: boolean;
```

- *Type:* boolean
- *Default:* true if ``removalPolicy`` is RETAIN, false otherwise

Indicates whether the DB instance should have deletion protection enabled.

---

##### `domain`<sup>Optional</sup> <a name="domain" id="pgstac-cdk-construct.Props.property.domain"></a>

```typescript
public readonly domain: string;
```

- *Type:* string
- *Default:* Do not join domain

The Active Directory directory ID to create the DB instance in.

---

##### `domainRole`<sup>Optional</sup> <a name="domainRole" id="pgstac-cdk-construct.Props.property.domainRole"></a>

```typescript
public readonly domainRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* The role will be created for you if {@link DatabaseInstanceNewProps#domain} is specified

The IAM role to be used when making API calls to the Directory Service.

The role needs the AWS-managed policy
AmazonRDSDirectoryServiceAccess or equivalent.

---

##### `enablePerformanceInsights`<sup>Optional</sup> <a name="enablePerformanceInsights" id="pgstac-cdk-construct.Props.property.enablePerformanceInsights"></a>

```typescript
public readonly enablePerformanceInsights: boolean;
```

- *Type:* boolean
- *Default:* false, unless ``performanceInsightRentention`` or ``performanceInsightEncryptionKey`` is set.

Whether to enable Performance Insights for the DB instance.

---

##### `iamAuthentication`<sup>Optional</sup> <a name="iamAuthentication" id="pgstac-cdk-construct.Props.property.iamAuthentication"></a>

```typescript
public readonly iamAuthentication: boolean;
```

- *Type:* boolean
- *Default:* false

Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

---

##### `instanceIdentifier`<sup>Optional</sup> <a name="instanceIdentifier" id="pgstac-cdk-construct.Props.property.instanceIdentifier"></a>

```typescript
public readonly instanceIdentifier: string;
```

- *Type:* string
- *Default:* a CloudFormation generated name

A name for the DB instance.

If you specify a name, AWS CloudFormation
converts it to lowercase.

---

##### `iops`<sup>Optional</sup> <a name="iops" id="pgstac-cdk-construct.Props.property.iops"></a>

```typescript
public readonly iops: number;
```

- *Type:* number
- *Default:* no provisioned iops

The number of I/O operations per second (IOPS) that the database provisions.

The value must be equal to or greater than 1000.

---

##### `maxAllocatedStorage`<sup>Optional</sup> <a name="maxAllocatedStorage" id="pgstac-cdk-construct.Props.property.maxAllocatedStorage"></a>

```typescript
public readonly maxAllocatedStorage: number;
```

- *Type:* number
- *Default:* No autoscaling of RDS instance

Upper limit to which RDS can scale the storage in GiB(Gibibyte).

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html#USER_PIOPS.Autoscaling](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html#USER_PIOPS.Autoscaling)

---

##### `monitoringInterval`<sup>Optional</sup> <a name="monitoringInterval" id="pgstac-cdk-construct.Props.property.monitoringInterval"></a>

```typescript
public readonly monitoringInterval: Duration;
```

- *Type:* aws-cdk-lib.Duration
- *Default:* no enhanced monitoring

The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance.

---

##### `monitoringRole`<sup>Optional</sup> <a name="monitoringRole" id="pgstac-cdk-construct.Props.property.monitoringRole"></a>

```typescript
public readonly monitoringRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* A role is automatically created for you

Role that will be used to manage DB instance monitoring.

---

##### `multiAz`<sup>Optional</sup> <a name="multiAz" id="pgstac-cdk-construct.Props.property.multiAz"></a>

```typescript
public readonly multiAz: boolean;
```

- *Type:* boolean
- *Default:* false

Specifies if the database instance is a multiple Availability Zone deployment.

---

##### `optionGroup`<sup>Optional</sup> <a name="optionGroup" id="pgstac-cdk-construct.Props.property.optionGroup"></a>

```typescript
public readonly optionGroup: IOptionGroup;
```

- *Type:* aws-cdk-lib.aws_rds.IOptionGroup
- *Default:* no option group

The option group to associate with the instance.

---

##### `parameterGroup`<sup>Optional</sup> <a name="parameterGroup" id="pgstac-cdk-construct.Props.property.parameterGroup"></a>

```typescript
public readonly parameterGroup: IParameterGroup;
```

- *Type:* aws-cdk-lib.aws_rds.IParameterGroup
- *Default:* no parameter group

The DB parameter group to associate with the instance.

---

##### `performanceInsightEncryptionKey`<sup>Optional</sup> <a name="performanceInsightEncryptionKey" id="pgstac-cdk-construct.Props.property.performanceInsightEncryptionKey"></a>

```typescript
public readonly performanceInsightEncryptionKey: IKey;
```

- *Type:* aws-cdk-lib.aws_kms.IKey
- *Default:* default master key

The AWS KMS key for encryption of Performance Insights data.

---

##### `performanceInsightRetention`<sup>Optional</sup> <a name="performanceInsightRetention" id="pgstac-cdk-construct.Props.property.performanceInsightRetention"></a>

```typescript
public readonly performanceInsightRetention: PerformanceInsightRetention;
```

- *Type:* aws-cdk-lib.aws_rds.PerformanceInsightRetention
- *Default:* 7

The amount of time, in days, to retain Performance Insights data.

---

##### `port`<sup>Optional</sup> <a name="port" id="pgstac-cdk-construct.Props.property.port"></a>

```typescript
public readonly port: number;
```

- *Type:* number
- *Default:* the default port for the chosen engine.

The port for the instance.

---

##### `preferredBackupWindow`<sup>Optional</sup> <a name="preferredBackupWindow" id="pgstac-cdk-construct.Props.property.preferredBackupWindow"></a>

```typescript
public readonly preferredBackupWindow: string;
```

- *Type:* string
- *Default:* a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html#USER_WorkingWithAutomatedBackups.BackupWindow

The daily time range during which automated backups are performed.

Constraints:
- Must be in the format `hh24:mi-hh24:mi`.
- Must be in Universal Coordinated Time (UTC).
- Must not conflict with the preferred maintenance window.
- Must be at least 30 minutes.

---

##### `preferredMaintenanceWindow`<sup>Optional</sup> <a name="preferredMaintenanceWindow" id="pgstac-cdk-construct.Props.property.preferredMaintenanceWindow"></a>

```typescript
public readonly preferredMaintenanceWindow: string;
```

- *Type:* string
- *Default:* a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#Concepts.DBMaintenance

The weekly time range (in UTC) during which system maintenance can occur.

Format: `ddd:hh24:mi-ddd:hh24:mi`
Constraint: Minimum 30-minute window

---

##### `processorFeatures`<sup>Optional</sup> <a name="processorFeatures" id="pgstac-cdk-construct.Props.property.processorFeatures"></a>

```typescript
public readonly processorFeatures: ProcessorFeatures;
```

- *Type:* aws-cdk-lib.aws_rds.ProcessorFeatures
- *Default:* the default number of CPU cores and threads per core for the chosen instance class.  See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor

The number of CPU cores and the number of threads per core.

---

##### `publiclyAccessible`<sup>Optional</sup> <a name="publiclyAccessible" id="pgstac-cdk-construct.Props.property.publiclyAccessible"></a>

```typescript
public readonly publiclyAccessible: boolean;
```

- *Type:* boolean
- *Default:* `true` if `vpcSubnets` is `subnetType: SubnetType.PUBLIC`, `false` otherwise

Indicates whether the DB instance is an internet-facing instance.

---

##### `removalPolicy`<sup>Optional</sup> <a name="removalPolicy" id="pgstac-cdk-construct.Props.property.removalPolicy"></a>

```typescript
public readonly removalPolicy: RemovalPolicy;
```

- *Type:* aws-cdk-lib.RemovalPolicy
- *Default:* RemovalPolicy.SNAPSHOT (remove the resource, but retain a snapshot of the data)

The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update.

---

##### `s3ExportBuckets`<sup>Optional</sup> <a name="s3ExportBuckets" id="pgstac-cdk-construct.Props.property.s3ExportBuckets"></a>

```typescript
public readonly s3ExportBuckets: IBucket[];
```

- *Type:* aws-cdk-lib.aws_s3.IBucket[]
- *Default:* None

S3 buckets that you want to load data into.

This property must not be used if `s3ExportRole` is used.

For Microsoft SQL Server:

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-s3-integration.html](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-s3-integration.html)

---

##### `s3ExportRole`<sup>Optional</sup> <a name="s3ExportRole" id="pgstac-cdk-construct.Props.property.s3ExportRole"></a>

```typescript
public readonly s3ExportRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* New role is created if `s3ExportBuckets` is set, no role is defined otherwise

Role that will be associated with this DB instance to enable S3 export.

This property must not be used if `s3ExportBuckets` is used.

For Microsoft SQL Server:

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-s3-integration.html](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-s3-integration.html)

---

##### `s3ImportBuckets`<sup>Optional</sup> <a name="s3ImportBuckets" id="pgstac-cdk-construct.Props.property.s3ImportBuckets"></a>

```typescript
public readonly s3ImportBuckets: IBucket[];
```

- *Type:* aws-cdk-lib.aws_s3.IBucket[]
- *Default:* None

S3 buckets that you want to load data from.

This feature is only supported by the Microsoft SQL Server, Oracle, and PostgreSQL engines.

This property must not be used if `s3ImportRole` is used.

For Microsoft SQL Server:

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Procedural.Importing.html](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Procedural.Importing.html)

---

##### `s3ImportRole`<sup>Optional</sup> <a name="s3ImportRole" id="pgstac-cdk-construct.Props.property.s3ImportRole"></a>

```typescript
public readonly s3ImportRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* New role is created if `s3ImportBuckets` is set, no role is defined otherwise

Role that will be associated with this DB instance to enable S3 import.

This feature is only supported by the Microsoft SQL Server, Oracle, and PostgreSQL engines.

This property must not be used if `s3ImportBuckets` is used.

For Microsoft SQL Server:

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Procedural.Importing.html](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Procedural.Importing.html)

---

##### `securityGroups`<sup>Optional</sup> <a name="securityGroups" id="pgstac-cdk-construct.Props.property.securityGroups"></a>

```typescript
public readonly securityGroups: ISecurityGroup[];
```

- *Type:* aws-cdk-lib.aws_ec2.ISecurityGroup[]
- *Default:* a new security group is created

The security groups to assign to the DB instance.

---

##### `storageType`<sup>Optional</sup> <a name="storageType" id="pgstac-cdk-construct.Props.property.storageType"></a>

```typescript
public readonly storageType: StorageType;
```

- *Type:* aws-cdk-lib.aws_rds.StorageType
- *Default:* GP2

The storage type.

Storage types supported are gp2, io1, standard.

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#Concepts.Storage.GeneralSSD](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#Concepts.Storage.GeneralSSD)

---

##### `subnetGroup`<sup>Optional</sup> <a name="subnetGroup" id="pgstac-cdk-construct.Props.property.subnetGroup"></a>

```typescript
public readonly subnetGroup: ISubnetGroup;
```

- *Type:* aws-cdk-lib.aws_rds.ISubnetGroup
- *Default:* a new subnet group will be created.

Existing subnet group for the instance.

---

##### `vpcSubnets`<sup>Optional</sup> <a name="vpcSubnets" id="pgstac-cdk-construct.Props.property.vpcSubnets"></a>

```typescript
public readonly vpcSubnets: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection
- *Default:* private subnets

The type of subnets to add to the created DB subnet group.

---

##### `engine`<sup>Required</sup> <a name="engine" id="pgstac-cdk-construct.Props.property.engine"></a>

```typescript
public readonly engine: IInstanceEngine;
```

- *Type:* aws-cdk-lib.aws_rds.IInstanceEngine

The database engine.

---

##### `allocatedStorage`<sup>Optional</sup> <a name="allocatedStorage" id="pgstac-cdk-construct.Props.property.allocatedStorage"></a>

```typescript
public readonly allocatedStorage: number;
```

- *Type:* number
- *Default:* 100

The allocated storage size, specified in gibibytes (GiB).

---

##### `allowMajorVersionUpgrade`<sup>Optional</sup> <a name="allowMajorVersionUpgrade" id="pgstac-cdk-construct.Props.property.allowMajorVersionUpgrade"></a>

```typescript
public readonly allowMajorVersionUpgrade: boolean;
```

- *Type:* boolean
- *Default:* false

Whether to allow major version upgrades.

---

##### `databaseName`<sup>Optional</sup> <a name="databaseName" id="pgstac-cdk-construct.Props.property.databaseName"></a>

```typescript
public readonly databaseName: string;
```

- *Type:* string
- *Default:* no name

The name of the database.

---

##### `instanceType`<sup>Optional</sup> <a name="instanceType" id="pgstac-cdk-construct.Props.property.instanceType"></a>

```typescript
public readonly instanceType: InstanceType;
```

- *Type:* aws-cdk-lib.aws_ec2.InstanceType
- *Default:* m5.large (or, more specifically, db.m5.large)

The name of the compute and memory capacity for the instance.

---

##### `licenseModel`<sup>Optional</sup> <a name="licenseModel" id="pgstac-cdk-construct.Props.property.licenseModel"></a>

```typescript
public readonly licenseModel: LicenseModel;
```

- *Type:* aws-cdk-lib.aws_rds.LicenseModel
- *Default:* RDS default license model

The license model.

---

##### `parameters`<sup>Optional</sup> <a name="parameters" id="pgstac-cdk-construct.Props.property.parameters"></a>

```typescript
public readonly parameters: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}
- *Default:* None

The parameters in the DBParameterGroup to create automatically.

You can only specify parameterGroup or parameters but not both.
You need to use a versioned engine to auto-generate a DBParameterGroup.

---

##### `timezone`<sup>Optional</sup> <a name="timezone" id="pgstac-cdk-construct.Props.property.timezone"></a>

```typescript
public readonly timezone: string;
```

- *Type:* string
- *Default:* RDS default timezone

The time zone of the instance.

This is currently supported only by Microsoft Sql Server.

---

##### `characterSetName`<sup>Optional</sup> <a name="characterSetName" id="pgstac-cdk-construct.Props.property.characterSetName"></a>

```typescript
public readonly characterSetName: string;
```

- *Type:* string
- *Default:* RDS default character set name

For supported engines, specifies the character set to associate with the DB instance.

---

##### `credentials`<sup>Optional</sup> <a name="credentials" id="pgstac-cdk-construct.Props.property.credentials"></a>

```typescript
public readonly credentials: Credentials;
```

- *Type:* aws-cdk-lib.aws_rds.Credentials
- *Default:* A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password

Credentials for the administrative user.

---

##### `storageEncrypted`<sup>Optional</sup> <a name="storageEncrypted" id="pgstac-cdk-construct.Props.property.storageEncrypted"></a>

```typescript
public readonly storageEncrypted: boolean;
```

- *Type:* boolean
- *Default:* true if storageEncryptionKey has been provided, false otherwise

Indicates whether the DB instance is encrypted.

---

##### `storageEncryptionKey`<sup>Optional</sup> <a name="storageEncryptionKey" id="pgstac-cdk-construct.Props.property.storageEncryptionKey"></a>

```typescript
public readonly storageEncryptionKey: IKey;
```

- *Type:* aws-cdk-lib.aws_kms.IKey
- *Default:* default master key if storageEncrypted is true, no key otherwise

The KMS key that's used to encrypt the DB instance.

---



