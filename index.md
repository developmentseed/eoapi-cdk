# API Reference <a name="API Reference" id="api-reference"></a>

## Constructs <a name="Constructs" id="Constructs"></a>

### BastionHost <a name="BastionHost" id="eoapi-cdk.BastionHost"></a>

The database is located in an isolated subnet, meaning that it is not accessible from the public internet.

As such, to interact with the database directly, a user must tunnel through a bastion host.

### Configuring

This codebase controls _who_ is allowed to connect to the bastion host. This requires two steps:

1. Adding the IP address from which you are connecting to the `ipv4Allowlist` array
1. Creating a bastion host system user by adding the user's configuration inform to `userdata.yaml`

#### Adding an IP address to the `ipv4Allowlist` array

The `BastionHost` construct takes in an `ipv4Allowlist` array as an argument. Find your IP address (eg `curl api.ipify.org`) and add that to the array along with the trailing CIDR block (likely `/32` to indicate that you are adding a single IP address).

#### Creating a user via `userdata.yaml`

Add an entry to the `users` array with a username (likely matching your local systems username, which you can get by running the `whoami` command in your terminal) and a public key (likely your default public key, which you can get by running `cat ~/.ssh/id_*.pub` in your terminal).

#### Tips & Tricks when using the Bastion Host

**Connecting to RDS Instance via SSM**

```sh
aws ssm start-session --target $INSTANCE_ID \
--document-name AWS-StartPortForwardingSessionToRemoteHost \
--parameters '{
"host": [
"example-db.c5abcdefghij.us-west-2.rds.amazonaws.com"
],
"portNumber": [
"5432"
],
"localPortNumber": [
"9999"
]
}' \
--profile $AWS_PROFILE
```

```sh
psql -h localhost -p 9999 # continue adding username (-U) and db (-d) here...
```

Connect directly to Bastion Host:

```sh
aws ssm start-session --target $INSTANCE_ID --profile $AWS_PROFILE
```

**Setting up an SSH tunnel**

In your `~/.ssh/config` file, add an entry like:

```
Host db-tunnel
Hostname {the-bastion-host-address}
LocalForward 9999 {the-db-hostname}:5432
```

Then a tunnel can be opened via:

```
ssh -N db-tunnel
```

And a connection to the DB can be made via:

```
psql -h 127.0.0.1 -p 9999 -U {username} -d {database}
```

**Handling `REMOTE HOST IDENTIFICATION HAS CHANGED!` error**

If you've redeployed a bastion host that you've previously connected to, you may see an error like:

```

#### Initializers <a name="Initializers" id="eoapi-cdk.BastionHost.Initializer"></a>

```typescript
import { BastionHost } from 'eoapi-cdk'

new BastionHost(scope: Construct, id: string, props: BastionHostProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.BastionHost.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.BastionHost.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.BastionHost.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.BastionHostProps">BastionHostProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.BastionHost.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.BastionHost.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.BastionHost.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.BastionHostProps">BastionHostProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.BastionHost.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="eoapi-cdk.BastionHost.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.BastionHost.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.BastionHost.isConstruct"></a>

```typescript
import { BastionHost } from 'eoapi-cdk'

BastionHost.isConstruct(x: any)
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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.BastionHost.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.BastionHost.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.BastionHost.property.instance">instance</a></code> | <code>aws-cdk-lib.aws_ec2.Instance</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.BastionHost.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `instance`<sup>Required</sup> <a name="instance" id="eoapi-cdk.BastionHost.property.instance"></a>

```typescript
public readonly instance: Instance;
```

- *Type:* aws-cdk-lib.aws_ec2.Instance

---


### PgStacApiLambda <a name="PgStacApiLambda" id="eoapi-cdk.PgStacApiLambda"></a>

#### Initializers <a name="Initializers" id="eoapi-cdk.PgStacApiLambda.Initializer"></a>

```typescript
import { PgStacApiLambda } from 'eoapi-cdk'

new PgStacApiLambda(scope: Construct, id: string, props: PgStacApiLambdaProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.PgStacApiLambda.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacApiLambda.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacApiLambda.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.PgStacApiLambdaProps">PgStacApiLambdaProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.PgStacApiLambda.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.PgStacApiLambda.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.PgStacApiLambda.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.PgStacApiLambdaProps">PgStacApiLambdaProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.PgStacApiLambda.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="eoapi-cdk.PgStacApiLambda.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.PgStacApiLambda.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.PgStacApiLambda.isConstruct"></a>

```typescript
import { PgStacApiLambda } from 'eoapi-cdk'

PgStacApiLambda.isConstruct(x: any)
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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.PgStacApiLambda.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.PgStacApiLambda.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.PgStacApiLambda.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacApiLambda.property.stacApiLambdaFunction">stacApiLambdaFunction</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.PgStacApiLambda.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `url`<sup>Required</sup> <a name="url" id="eoapi-cdk.PgStacApiLambda.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `stacApiLambdaFunction`<sup>Required</sup> <a name="stacApiLambdaFunction" id="eoapi-cdk.PgStacApiLambda.property.stacApiLambdaFunction"></a>

```typescript
public readonly stacApiLambdaFunction: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---


### PgStacDatabase <a name="PgStacDatabase" id="eoapi-cdk.PgStacDatabase"></a>

An RDS instance with pgSTAC installed.

This is a wrapper around the
`rds.DatabaseInstance` higher-level construct making use
of the BootstrapPgStac construct.

#### Initializers <a name="Initializers" id="eoapi-cdk.PgStacDatabase.Initializer"></a>

```typescript
import { PgStacDatabase } from 'eoapi-cdk'

new PgStacDatabase(scope: Construct, id: string, props: PgStacDatabaseProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.PgStacDatabase.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacDatabase.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacDatabase.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.PgStacDatabaseProps">PgStacDatabaseProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.PgStacDatabase.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.PgStacDatabase.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.PgStacDatabase.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.PgStacDatabaseProps">PgStacDatabaseProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.PgStacDatabase.toString">toString</a></code> | Returns a string representation of this construct. |
| <code><a href="#eoapi-cdk.PgStacDatabase.getParameters">getParameters</a></code> | *No description.* |

---

##### `toString` <a name="toString" id="eoapi-cdk.PgStacDatabase.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

##### `getParameters` <a name="getParameters" id="eoapi-cdk.PgStacDatabase.getParameters"></a>

```typescript
public getParameters(instanceType: string, parameters?: {[ key: string ]: string}): DatabaseParameters
```

###### `instanceType`<sup>Required</sup> <a name="instanceType" id="eoapi-cdk.PgStacDatabase.getParameters.parameter.instanceType"></a>

- *Type:* string

---

###### `parameters`<sup>Optional</sup> <a name="parameters" id="eoapi-cdk.PgStacDatabase.getParameters.parameter.parameters"></a>

- *Type:* {[ key: string ]: string}

---

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.PgStacDatabase.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.PgStacDatabase.isConstruct"></a>

```typescript
import { PgStacDatabase } from 'eoapi-cdk'

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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.PgStacDatabase.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.PgStacDatabase.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.PgStacDatabase.property.connectionTarget">connectionTarget</a></code> | <code>aws-cdk-lib.aws_ec2.Instance \| aws-cdk-lib.aws_rds.IDatabaseInstance</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacDatabase.property.securityGroup">securityGroup</a></code> | <code>aws-cdk-lib.aws_ec2.SecurityGroup</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacDatabase.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.DatabaseInstance</code> | *No description.* |
| <code><a href="#eoapi-cdk.PgStacDatabase.property.pgstacSecret">pgstacSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.PgStacDatabase.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `connectionTarget`<sup>Required</sup> <a name="connectionTarget" id="eoapi-cdk.PgStacDatabase.property.connectionTarget"></a>

```typescript
public readonly connectionTarget: Instance | IDatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_ec2.Instance | aws-cdk-lib.aws_rds.IDatabaseInstance

---

##### `securityGroup`<sup>Optional</sup> <a name="securityGroup" id="eoapi-cdk.PgStacDatabase.property.securityGroup"></a>

```typescript
public readonly securityGroup: SecurityGroup;
```

- *Type:* aws-cdk-lib.aws_ec2.SecurityGroup

---

##### `db`<sup>Required</sup> <a name="db" id="eoapi-cdk.PgStacDatabase.property.db"></a>

```typescript
public readonly db: DatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.DatabaseInstance

---

##### `pgstacSecret`<sup>Required</sup> <a name="pgstacSecret" id="eoapi-cdk.PgStacDatabase.property.pgstacSecret"></a>

```typescript
public readonly pgstacSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

---


### StacBrowser <a name="StacBrowser" id="eoapi-cdk.StacBrowser"></a>

#### Initializers <a name="Initializers" id="eoapi-cdk.StacBrowser.Initializer"></a>

```typescript
import { StacBrowser } from 'eoapi-cdk'

new StacBrowser(scope: Construct, id: string, props: StacBrowserProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.StacBrowser.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.StacBrowser.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.StacBrowser.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.StacBrowserProps">StacBrowserProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.StacBrowser.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.StacBrowser.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.StacBrowser.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.StacBrowserProps">StacBrowserProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.StacBrowser.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="eoapi-cdk.StacBrowser.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.StacBrowser.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.StacBrowser.isConstruct"></a>

```typescript
import { StacBrowser } from 'eoapi-cdk'

StacBrowser.isConstruct(x: any)
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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.StacBrowser.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.StacBrowser.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.StacBrowser.property.bucket">bucket</a></code> | <code>aws-cdk-lib.aws_s3.IBucket</code> | *No description.* |
| <code><a href="#eoapi-cdk.StacBrowser.property.bucketDeployment">bucketDeployment</a></code> | <code>aws-cdk-lib.aws_s3_deployment.BucketDeployment</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.StacBrowser.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `bucket`<sup>Required</sup> <a name="bucket" id="eoapi-cdk.StacBrowser.property.bucket"></a>

```typescript
public readonly bucket: IBucket;
```

- *Type:* aws-cdk-lib.aws_s3.IBucket

---

##### `bucketDeployment`<sup>Required</sup> <a name="bucketDeployment" id="eoapi-cdk.StacBrowser.property.bucketDeployment"></a>

```typescript
public readonly bucketDeployment: BucketDeployment;
```

- *Type:* aws-cdk-lib.aws_s3_deployment.BucketDeployment

---


### StacIngestor <a name="StacIngestor" id="eoapi-cdk.StacIngestor"></a>

#### Initializers <a name="Initializers" id="eoapi-cdk.StacIngestor.Initializer"></a>

```typescript
import { StacIngestor } from 'eoapi-cdk'

new StacIngestor(scope: Construct, id: string, props: StacIngestorProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.StacIngestor.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.StacIngestor.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.StacIngestor.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.StacIngestorProps">StacIngestorProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.StacIngestor.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.StacIngestor.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.StacIngestor.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.StacIngestorProps">StacIngestorProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.StacIngestor.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="eoapi-cdk.StacIngestor.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.StacIngestor.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.StacIngestor.isConstruct"></a>

```typescript
import { StacIngestor } from 'eoapi-cdk'

StacIngestor.isConstruct(x: any)
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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.StacIngestor.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.StacIngestor.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.StacIngestor.property.handlerRole">handlerRole</a></code> | <code>aws-cdk-lib.aws_iam.Role</code> | *No description.* |
| <code><a href="#eoapi-cdk.StacIngestor.property.table">table</a></code> | <code>aws-cdk-lib.aws_dynamodb.Table</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.StacIngestor.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `handlerRole`<sup>Required</sup> <a name="handlerRole" id="eoapi-cdk.StacIngestor.property.handlerRole"></a>

```typescript
public readonly handlerRole: Role;
```

- *Type:* aws-cdk-lib.aws_iam.Role

---

##### `table`<sup>Required</sup> <a name="table" id="eoapi-cdk.StacIngestor.property.table"></a>

```typescript
public readonly table: Table;
```

- *Type:* aws-cdk-lib.aws_dynamodb.Table

---


### TiPgApiLambda <a name="TiPgApiLambda" id="eoapi-cdk.TiPgApiLambda"></a>

#### Initializers <a name="Initializers" id="eoapi-cdk.TiPgApiLambda.Initializer"></a>

```typescript
import { TiPgApiLambda } from 'eoapi-cdk'

new TiPgApiLambda(scope: Construct, id: string, props: TiPgApiLambdaProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.TiPgApiLambda.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.TiPgApiLambda.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.TiPgApiLambda.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.TiPgApiLambdaProps">TiPgApiLambdaProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.TiPgApiLambda.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.TiPgApiLambda.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.TiPgApiLambda.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.TiPgApiLambdaProps">TiPgApiLambdaProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.TiPgApiLambda.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="eoapi-cdk.TiPgApiLambda.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.TiPgApiLambda.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.TiPgApiLambda.isConstruct"></a>

```typescript
import { TiPgApiLambda } from 'eoapi-cdk'

TiPgApiLambda.isConstruct(x: any)
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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.TiPgApiLambda.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.TiPgApiLambda.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.TiPgApiLambda.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.TiPgApiLambda.property.tiPgLambdaFunction">tiPgLambdaFunction</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.TiPgApiLambda.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `url`<sup>Required</sup> <a name="url" id="eoapi-cdk.TiPgApiLambda.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `tiPgLambdaFunction`<sup>Required</sup> <a name="tiPgLambdaFunction" id="eoapi-cdk.TiPgApiLambda.property.tiPgLambdaFunction"></a>

```typescript
public readonly tiPgLambdaFunction: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---


### TitilerPgstacApiLambda <a name="TitilerPgstacApiLambda" id="eoapi-cdk.TitilerPgstacApiLambda"></a>

#### Initializers <a name="Initializers" id="eoapi-cdk.TitilerPgstacApiLambda.Initializer"></a>

```typescript
import { TitilerPgstacApiLambda } from 'eoapi-cdk'

new TitilerPgstacApiLambda(scope: Construct, id: string, props: TitilerPgStacApiLambdaProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.Initializer.parameter.props">props</a></code> | <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps">TitilerPgStacApiLambdaProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="eoapi-cdk.TitilerPgstacApiLambda.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="eoapi-cdk.TitilerPgstacApiLambda.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="eoapi-cdk.TitilerPgstacApiLambda.Initializer.parameter.props"></a>

- *Type:* <a href="#eoapi-cdk.TitilerPgStacApiLambdaProps">TitilerPgStacApiLambdaProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="eoapi-cdk.TitilerPgstacApiLambda.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="eoapi-cdk.TitilerPgstacApiLambda.isConstruct"></a>

```typescript
import { TitilerPgstacApiLambda } from 'eoapi-cdk'

TitilerPgstacApiLambda.isConstruct(x: any)
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

###### `x`<sup>Required</sup> <a name="x" id="eoapi-cdk.TitilerPgstacApiLambda.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.TitilerPgstacApiLambda.property.titilerPgstacLambdaFunction">titilerPgstacLambdaFunction</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="eoapi-cdk.TitilerPgstacApiLambda.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `url`<sup>Required</sup> <a name="url" id="eoapi-cdk.TitilerPgstacApiLambda.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `titilerPgstacLambdaFunction`<sup>Required</sup> <a name="titilerPgstacLambdaFunction" id="eoapi-cdk.TitilerPgstacApiLambda.property.titilerPgstacLambdaFunction"></a>

```typescript
public readonly titilerPgstacLambdaFunction: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---


## Structs <a name="Structs" id="Structs"></a>

### BastionHostProps <a name="BastionHostProps" id="eoapi-cdk.BastionHostProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.BastionHostProps.Initializer"></a>

```typescript
import { BastionHostProps } from 'eoapi-cdk'

const bastionHostProps: BastionHostProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.BastionHostProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance</code> | *No description.* |
| <code><a href="#eoapi-cdk.BastionHostProps.property.ipv4Allowlist">ipv4Allowlist</a></code> | <code>string[]</code> | *No description.* |
| <code><a href="#eoapi-cdk.BastionHostProps.property.userData">userData</a></code> | <code>aws-cdk-lib.aws_ec2.UserData</code> | *No description.* |
| <code><a href="#eoapi-cdk.BastionHostProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | *No description.* |
| <code><a href="#eoapi-cdk.BastionHostProps.property.createElasticIp">createElasticIp</a></code> | <code>boolean</code> | Whether or not an elastic IP should be created for the bastion host. |
| <code><a href="#eoapi-cdk.BastionHostProps.property.sshPort">sshPort</a></code> | <code>number</code> | *No description.* |

---

##### `db`<sup>Required</sup> <a name="db" id="eoapi-cdk.BastionHostProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance

---

##### `ipv4Allowlist`<sup>Required</sup> <a name="ipv4Allowlist" id="eoapi-cdk.BastionHostProps.property.ipv4Allowlist"></a>

```typescript
public readonly ipv4Allowlist: string[];
```

- *Type:* string[]

---

##### `userData`<sup>Required</sup> <a name="userData" id="eoapi-cdk.BastionHostProps.property.userData"></a>

```typescript
public readonly userData: UserData;
```

- *Type:* aws-cdk-lib.aws_ec2.UserData

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="eoapi-cdk.BastionHostProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

---

##### `createElasticIp`<sup>Optional</sup> <a name="createElasticIp" id="eoapi-cdk.BastionHostProps.property.createElasticIp"></a>

```typescript
public readonly createElasticIp: boolean;
```

- *Type:* boolean
- *Default:* false

Whether or not an elastic IP should be created for the bastion host.

---

##### `sshPort`<sup>Optional</sup> <a name="sshPort" id="eoapi-cdk.BastionHostProps.property.sshPort"></a>

```typescript
public readonly sshPort: number;
```

- *Type:* number

---

### DatabaseParameters <a name="DatabaseParameters" id="eoapi-cdk.DatabaseParameters"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.DatabaseParameters.Initializer"></a>

```typescript
import { DatabaseParameters } from 'eoapi-cdk'

const databaseParameters: DatabaseParameters = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.effectiveCacheSize">effectiveCacheSize</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.maintenanceWorkMem">maintenanceWorkMem</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.maxConnections">maxConnections</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.maxLocksPerTransaction">maxLocksPerTransaction</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.randomPageCost">randomPageCost</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.seqPageCost">seqPageCost</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.sharedBuffers">sharedBuffers</a></code> | <code>string</code> | Note: This value is measured in 8KB blocks. |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.tempBuffers">tempBuffers</a></code> | <code>string</code> | *No description.* |
| <code><a href="#eoapi-cdk.DatabaseParameters.property.workMem">workMem</a></code> | <code>string</code> | *No description.* |

---

##### `effectiveCacheSize`<sup>Required</sup> <a name="effectiveCacheSize" id="eoapi-cdk.DatabaseParameters.property.effectiveCacheSize"></a>

```typescript
public readonly effectiveCacheSize: string;
```

- *Type:* string
- *Default:* 75% of instance memory

---

##### `maintenanceWorkMem`<sup>Required</sup> <a name="maintenanceWorkMem" id="eoapi-cdk.DatabaseParameters.property.maintenanceWorkMem"></a>

```typescript
public readonly maintenanceWorkMem: string;
```

- *Type:* string
- *Default:* 25% of shared buffers

---

##### `maxConnections`<sup>Required</sup> <a name="maxConnections" id="eoapi-cdk.DatabaseParameters.property.maxConnections"></a>

```typescript
public readonly maxConnections: string;
```

- *Type:* string
- *Default:* LEAST({DBInstanceClassMemory/9531392}, 5000)

---

##### `maxLocksPerTransaction`<sup>Required</sup> <a name="maxLocksPerTransaction" id="eoapi-cdk.DatabaseParameters.property.maxLocksPerTransaction"></a>

```typescript
public readonly maxLocksPerTransaction: string;
```

- *Type:* string
- *Default:* 1024

---

##### `randomPageCost`<sup>Required</sup> <a name="randomPageCost" id="eoapi-cdk.DatabaseParameters.property.randomPageCost"></a>

```typescript
public readonly randomPageCost: string;
```

- *Type:* string
- *Default:* 1.1

---

##### `seqPageCost`<sup>Required</sup> <a name="seqPageCost" id="eoapi-cdk.DatabaseParameters.property.seqPageCost"></a>

```typescript
public readonly seqPageCost: string;
```

- *Type:* string
- *Default:* 1

---

##### `sharedBuffers`<sup>Required</sup> <a name="sharedBuffers" id="eoapi-cdk.DatabaseParameters.property.sharedBuffers"></a>

```typescript
public readonly sharedBuffers: string;
```

- *Type:* string
- *Default:* '{DBInstanceClassMemory/32768}' 25% of instance memory, ie `{(DBInstanceClassMemory/(1024*8)) * 0.25}`

Note: This value is measured in 8KB blocks.

---

##### `tempBuffers`<sup>Required</sup> <a name="tempBuffers" id="eoapi-cdk.DatabaseParameters.property.tempBuffers"></a>

```typescript
public readonly tempBuffers: string;
```

- *Type:* string
- *Default:* 131172 (128 * 1024)

---

##### `workMem`<sup>Required</sup> <a name="workMem" id="eoapi-cdk.DatabaseParameters.property.workMem"></a>

```typescript
public readonly workMem: string;
```

- *Type:* string
- *Default:* shared buffers divided by max connections

---

### PgStacApiLambdaProps <a name="PgStacApiLambdaProps" id="eoapi-cdk.PgStacApiLambdaProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.PgStacApiLambdaProps.Initializer"></a>

```typescript
import { PgStacApiLambdaProps } from 'eoapi-cdk'

const pgStacApiLambdaProps: PgStacApiLambdaProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance \| aws-cdk-lib.aws_ec2.IInstance</code> | RDS Instance with installed pgSTAC or pgbouncer server. |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing connection information for pgSTAC database. |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Customized environment variables to send to fastapi-pgstac runtime. |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.lambdaFunctionOptions">lambdaFunctionOptions</a></code> | <code>any</code> | Can be used to override the default lambda function properties. |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.stacApiDomainName">stacApiDomainName</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.IDomainName</code> | Custom Domain Name Options for STAC API,. |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Subnet into which the lambda should be deployed. |
| <code><a href="#eoapi-cdk.PgStacApiLambdaProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC into which the lambda should be deployed. |

---

##### `db`<sup>Required</sup> <a name="db" id="eoapi-cdk.PgStacApiLambdaProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance | IInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance | aws-cdk-lib.aws_ec2.IInstance

RDS Instance with installed pgSTAC or pgbouncer server.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="eoapi-cdk.PgStacApiLambdaProps.property.dbSecret"></a>

```typescript
public readonly dbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing connection information for pgSTAC database.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="eoapi-cdk.PgStacApiLambdaProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Customized environment variables to send to fastapi-pgstac runtime.

---

##### `lambdaFunctionOptions`<sup>Optional</sup> <a name="lambdaFunctionOptions" id="eoapi-cdk.PgStacApiLambdaProps.property.lambdaFunctionOptions"></a>

```typescript
public readonly lambdaFunctionOptions: any;
```

- *Type:* any
- *Default:* defined in the construct.

Can be used to override the default lambda function properties.

---

##### `stacApiDomainName`<sup>Optional</sup> <a name="stacApiDomainName" id="eoapi-cdk.PgStacApiLambdaProps.property.stacApiDomainName"></a>

```typescript
public readonly stacApiDomainName: IDomainName;
```

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.IDomainName

Custom Domain Name Options for STAC API,.

---

##### `subnetSelection`<sup>Optional</sup> <a name="subnetSelection" id="eoapi-cdk.PgStacApiLambdaProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Subnet into which the lambda should be deployed.

---

##### `vpc`<sup>Optional</sup> <a name="vpc" id="eoapi-cdk.PgStacApiLambdaProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC into which the lambda should be deployed.

---

### PgStacDatabaseProps <a name="PgStacDatabaseProps" id="eoapi-cdk.PgStacDatabaseProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.PgStacDatabaseProps.Initializer"></a>

```typescript
import { PgStacDatabaseProps } from 'eoapi-cdk'

const pgStacDatabaseProps: PgStacDatabaseProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | The VPC network where the DB subnet group should be created. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.autoMinorVersionUpgrade">autoMinorVersionUpgrade</a></code> | <code>boolean</code> | Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.availabilityZone">availabilityZone</a></code> | <code>string</code> | The name of the Availability Zone where the DB instance will be located. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.backupRetention">backupRetention</a></code> | <code>aws-cdk-lib.Duration</code> | The number of days during which automatic DB snapshots are retained. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.caCertificate">caCertificate</a></code> | <code>aws-cdk-lib.aws_rds.CaCertificate</code> | The identifier of the CA certificate for this DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.cloudwatchLogsExports">cloudwatchLogsExports</a></code> | <code>string[]</code> | The list of log types that need to be enabled for exporting to CloudWatch Logs. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.cloudwatchLogsRetention">cloudwatchLogsRetention</a></code> | <code>aws-cdk-lib.aws_logs.RetentionDays</code> | The number of days log events are kept in CloudWatch Logs. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.cloudwatchLogsRetentionRole">cloudwatchLogsRetentionRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | The IAM role for the Lambda function associated with the custom resource that sets the retention policy. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.copyTagsToSnapshot">copyTagsToSnapshot</a></code> | <code>boolean</code> | Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.deleteAutomatedBackups">deleteAutomatedBackups</a></code> | <code>boolean</code> | Indicates whether automated backups should be deleted or retained when you delete a DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.deletionProtection">deletionProtection</a></code> | <code>boolean</code> | Indicates whether the DB instance should have deletion protection enabled. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.domain">domain</a></code> | <code>string</code> | The Active Directory directory ID to create the DB instance in. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.domainRole">domainRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | The IAM role to be used when making API calls to the Directory Service. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.enablePerformanceInsights">enablePerformanceInsights</a></code> | <code>boolean</code> | Whether to enable Performance Insights for the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.iamAuthentication">iamAuthentication</a></code> | <code>boolean</code> | Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.instanceIdentifier">instanceIdentifier</a></code> | <code>string</code> | A name for the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.iops">iops</a></code> | <code>number</code> | The number of I/O operations per second (IOPS) that the database provisions. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.maxAllocatedStorage">maxAllocatedStorage</a></code> | <code>number</code> | Upper limit to which RDS can scale the storage in GiB(Gibibyte). |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.monitoringInterval">monitoringInterval</a></code> | <code>aws-cdk-lib.Duration</code> | The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.monitoringRole">monitoringRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be used to manage DB instance monitoring. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.multiAz">multiAz</a></code> | <code>boolean</code> | Specifies if the database instance is a multiple Availability Zone deployment. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.networkType">networkType</a></code> | <code>aws-cdk-lib.aws_rds.NetworkType</code> | The network type of the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.optionGroup">optionGroup</a></code> | <code>aws-cdk-lib.aws_rds.IOptionGroup</code> | The option group to associate with the instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.parameterGroup">parameterGroup</a></code> | <code>aws-cdk-lib.aws_rds.IParameterGroup</code> | The DB parameter group to associate with the instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.performanceInsightEncryptionKey">performanceInsightEncryptionKey</a></code> | <code>aws-cdk-lib.aws_kms.IKey</code> | The AWS KMS key for encryption of Performance Insights data. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.performanceInsightRetention">performanceInsightRetention</a></code> | <code>aws-cdk-lib.aws_rds.PerformanceInsightRetention</code> | The amount of time, in days, to retain Performance Insights data. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.port">port</a></code> | <code>number</code> | The port for the instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.preferredBackupWindow">preferredBackupWindow</a></code> | <code>string</code> | The daily time range during which automated backups are performed. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.preferredMaintenanceWindow">preferredMaintenanceWindow</a></code> | <code>string</code> | The weekly time range (in UTC) during which system maintenance can occur. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.processorFeatures">processorFeatures</a></code> | <code>aws-cdk-lib.aws_rds.ProcessorFeatures</code> | The number of CPU cores and the number of threads per core. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.publiclyAccessible">publiclyAccessible</a></code> | <code>boolean</code> | Indicates whether the DB instance is an internet-facing instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.removalPolicy">removalPolicy</a></code> | <code>aws-cdk-lib.RemovalPolicy</code> | The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.s3ExportBuckets">s3ExportBuckets</a></code> | <code>aws-cdk-lib.aws_s3.IBucket[]</code> | S3 buckets that you want to load data into. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.s3ExportRole">s3ExportRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be associated with this DB instance to enable S3 export. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.s3ImportBuckets">s3ImportBuckets</a></code> | <code>aws-cdk-lib.aws_s3.IBucket[]</code> | S3 buckets that you want to load data from. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.s3ImportRole">s3ImportRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be associated with this DB instance to enable S3 import. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.securityGroups">securityGroups</a></code> | <code>aws-cdk-lib.aws_ec2.ISecurityGroup[]</code> | The security groups to assign to the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.storageThroughput">storageThroughput</a></code> | <code>number</code> | The storage throughput, specified in mebibytes per second (MiBps). |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.storageType">storageType</a></code> | <code>aws-cdk-lib.aws_rds.StorageType</code> | The storage type. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.subnetGroup">subnetGroup</a></code> | <code>aws-cdk-lib.aws_rds.ISubnetGroup</code> | Existing subnet group for the instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.vpcSubnets">vpcSubnets</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | The type of subnets to add to the created DB subnet group. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.engine">engine</a></code> | <code>aws-cdk-lib.aws_rds.IInstanceEngine</code> | The database engine. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.allocatedStorage">allocatedStorage</a></code> | <code>number</code> | The allocated storage size, specified in gibibytes (GiB). |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.allowMajorVersionUpgrade">allowMajorVersionUpgrade</a></code> | <code>boolean</code> | Whether to allow major version upgrades. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.databaseName">databaseName</a></code> | <code>string</code> | The name of the database. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.instanceType">instanceType</a></code> | <code>aws-cdk-lib.aws_ec2.InstanceType</code> | The name of the compute and memory capacity for the instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.licenseModel">licenseModel</a></code> | <code>aws-cdk-lib.aws_rds.LicenseModel</code> | The license model. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.parameters">parameters</a></code> | <code>{[ key: string ]: string}</code> | The parameters in the DBParameterGroup to create automatically. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.timezone">timezone</a></code> | <code>string</code> | The time zone of the instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.characterSetName">characterSetName</a></code> | <code>string</code> | For supported engines, specifies the character set to associate with the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.credentials">credentials</a></code> | <code>aws-cdk-lib.aws_rds.Credentials</code> | Credentials for the administrative user. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.storageEncrypted">storageEncrypted</a></code> | <code>boolean</code> | Indicates whether the DB instance is encrypted. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.storageEncryptionKey">storageEncryptionKey</a></code> | <code>aws-cdk-lib.aws_kms.IKey</code> | The KMS key that's used to encrypt the DB instance. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.addPgbouncer">addPgbouncer</a></code> | <code>boolean</code> | Add pgbouncer instance for managing traffic to the pgSTAC database. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.bootstrapperLambdaFunctionOptions">bootstrapperLambdaFunctionOptions</a></code> | <code>any</code> | Can be used to override the default lambda function properties. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.customResourceProperties">customResourceProperties</a></code> | <code>{[ key: string ]: any}</code> | Lambda function Custom Resource properties. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.pgstacDbName">pgstacDbName</a></code> | <code>string</code> | Name of database that is to be created and onto which pgSTAC will be installed. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.pgstacUsername">pgstacUsername</a></code> | <code>string</code> | Name of user that will be generated for connecting to the pgSTAC database. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.pgstacVersion">pgstacVersion</a></code> | <code>string</code> | Version of pgstac to install on the database. |
| <code><a href="#eoapi-cdk.PgStacDatabaseProps.property.secretsPrefix">secretsPrefix</a></code> | <code>string</code> | Prefix to assign to the generated `secrets_manager.Secret`. |

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="eoapi-cdk.PgStacDatabaseProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

The VPC network where the DB subnet group should be created.

---

##### `autoMinorVersionUpgrade`<sup>Optional</sup> <a name="autoMinorVersionUpgrade" id="eoapi-cdk.PgStacDatabaseProps.property.autoMinorVersionUpgrade"></a>

```typescript
public readonly autoMinorVersionUpgrade: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window.

---

##### `availabilityZone`<sup>Optional</sup> <a name="availabilityZone" id="eoapi-cdk.PgStacDatabaseProps.property.availabilityZone"></a>

```typescript
public readonly availabilityZone: string;
```

- *Type:* string
- *Default:* no preference

The name of the Availability Zone where the DB instance will be located.

---

##### `backupRetention`<sup>Optional</sup> <a name="backupRetention" id="eoapi-cdk.PgStacDatabaseProps.property.backupRetention"></a>

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

##### `caCertificate`<sup>Optional</sup> <a name="caCertificate" id="eoapi-cdk.PgStacDatabaseProps.property.caCertificate"></a>

```typescript
public readonly caCertificate: CaCertificate;
```

- *Type:* aws-cdk-lib.aws_rds.CaCertificate
- *Default:* RDS will choose a certificate authority

The identifier of the CA certificate for this DB instance.

Specifying or updating this property triggers a reboot.

For RDS DB engines:

> [https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL-certificate-rotation.html](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL-certificate-rotation.html)

---

##### `cloudwatchLogsExports`<sup>Optional</sup> <a name="cloudwatchLogsExports" id="eoapi-cdk.PgStacDatabaseProps.property.cloudwatchLogsExports"></a>

```typescript
public readonly cloudwatchLogsExports: string[];
```

- *Type:* string[]
- *Default:* no log exports

The list of log types that need to be enabled for exporting to CloudWatch Logs.

---

##### `cloudwatchLogsRetention`<sup>Optional</sup> <a name="cloudwatchLogsRetention" id="eoapi-cdk.PgStacDatabaseProps.property.cloudwatchLogsRetention"></a>

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

##### `cloudwatchLogsRetentionRole`<sup>Optional</sup> <a name="cloudwatchLogsRetentionRole" id="eoapi-cdk.PgStacDatabaseProps.property.cloudwatchLogsRetentionRole"></a>

```typescript
public readonly cloudwatchLogsRetentionRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* a new role is created.

The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

---

##### `copyTagsToSnapshot`<sup>Optional</sup> <a name="copyTagsToSnapshot" id="eoapi-cdk.PgStacDatabaseProps.property.copyTagsToSnapshot"></a>

```typescript
public readonly copyTagsToSnapshot: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance.

---

##### `deleteAutomatedBackups`<sup>Optional</sup> <a name="deleteAutomatedBackups" id="eoapi-cdk.PgStacDatabaseProps.property.deleteAutomatedBackups"></a>

```typescript
public readonly deleteAutomatedBackups: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates whether automated backups should be deleted or retained when you delete a DB instance.

---

##### `deletionProtection`<sup>Optional</sup> <a name="deletionProtection" id="eoapi-cdk.PgStacDatabaseProps.property.deletionProtection"></a>

```typescript
public readonly deletionProtection: boolean;
```

- *Type:* boolean
- *Default:* true if ``removalPolicy`` is RETAIN, false otherwise

Indicates whether the DB instance should have deletion protection enabled.

---

##### `domain`<sup>Optional</sup> <a name="domain" id="eoapi-cdk.PgStacDatabaseProps.property.domain"></a>

```typescript
public readonly domain: string;
```

- *Type:* string
- *Default:* Do not join domain

The Active Directory directory ID to create the DB instance in.

---

##### `domainRole`<sup>Optional</sup> <a name="domainRole" id="eoapi-cdk.PgStacDatabaseProps.property.domainRole"></a>

```typescript
public readonly domainRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* The role will be created for you if `DatabaseInstanceNewProps#domain` is specified

The IAM role to be used when making API calls to the Directory Service.

The role needs the AWS-managed policy
AmazonRDSDirectoryServiceAccess or equivalent.

---

##### `enablePerformanceInsights`<sup>Optional</sup> <a name="enablePerformanceInsights" id="eoapi-cdk.PgStacDatabaseProps.property.enablePerformanceInsights"></a>

```typescript
public readonly enablePerformanceInsights: boolean;
```

- *Type:* boolean
- *Default:* false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set.

Whether to enable Performance Insights for the DB instance.

---

##### `iamAuthentication`<sup>Optional</sup> <a name="iamAuthentication" id="eoapi-cdk.PgStacDatabaseProps.property.iamAuthentication"></a>

```typescript
public readonly iamAuthentication: boolean;
```

- *Type:* boolean
- *Default:* false

Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

---

##### `instanceIdentifier`<sup>Optional</sup> <a name="instanceIdentifier" id="eoapi-cdk.PgStacDatabaseProps.property.instanceIdentifier"></a>

```typescript
public readonly instanceIdentifier: string;
```

- *Type:* string
- *Default:* a CloudFormation generated name

A name for the DB instance.

If you specify a name, AWS CloudFormation
converts it to lowercase.

---

##### `iops`<sup>Optional</sup> <a name="iops" id="eoapi-cdk.PgStacDatabaseProps.property.iops"></a>

```typescript
public readonly iops: number;
```

- *Type:* number
- *Default:* no provisioned iops if storage type is not specified. For GP3: 3,000 IOPS if allocated storage is less than 400 GiB for MariaDB, MySQL, and PostgreSQL, less than 200 GiB for Oracle and less than 20 GiB for SQL Server. 12,000 IOPS otherwise (except for SQL Server where the default is always 3,000 IOPS).

The number of I/O operations per second (IOPS) that the database provisions.

The value must be equal to or greater than 1000.

---

##### `maxAllocatedStorage`<sup>Optional</sup> <a name="maxAllocatedStorage" id="eoapi-cdk.PgStacDatabaseProps.property.maxAllocatedStorage"></a>

```typescript
public readonly maxAllocatedStorage: number;
```

- *Type:* number
- *Default:* No autoscaling of RDS instance

Upper limit to which RDS can scale the storage in GiB(Gibibyte).

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html#USER_PIOPS.Autoscaling](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html#USER_PIOPS.Autoscaling)

---

##### `monitoringInterval`<sup>Optional</sup> <a name="monitoringInterval" id="eoapi-cdk.PgStacDatabaseProps.property.monitoringInterval"></a>

```typescript
public readonly monitoringInterval: Duration;
```

- *Type:* aws-cdk-lib.Duration
- *Default:* no enhanced monitoring

The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance.

---

##### `monitoringRole`<sup>Optional</sup> <a name="monitoringRole" id="eoapi-cdk.PgStacDatabaseProps.property.monitoringRole"></a>

```typescript
public readonly monitoringRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* A role is automatically created for you

Role that will be used to manage DB instance monitoring.

---

##### `multiAz`<sup>Optional</sup> <a name="multiAz" id="eoapi-cdk.PgStacDatabaseProps.property.multiAz"></a>

```typescript
public readonly multiAz: boolean;
```

- *Type:* boolean
- *Default:* false

Specifies if the database instance is a multiple Availability Zone deployment.

---

##### `networkType`<sup>Optional</sup> <a name="networkType" id="eoapi-cdk.PgStacDatabaseProps.property.networkType"></a>

```typescript
public readonly networkType: NetworkType;
```

- *Type:* aws-cdk-lib.aws_rds.NetworkType
- *Default:* IPV4

The network type of the DB instance.

---

##### `optionGroup`<sup>Optional</sup> <a name="optionGroup" id="eoapi-cdk.PgStacDatabaseProps.property.optionGroup"></a>

```typescript
public readonly optionGroup: IOptionGroup;
```

- *Type:* aws-cdk-lib.aws_rds.IOptionGroup
- *Default:* no option group

The option group to associate with the instance.

---

##### `parameterGroup`<sup>Optional</sup> <a name="parameterGroup" id="eoapi-cdk.PgStacDatabaseProps.property.parameterGroup"></a>

```typescript
public readonly parameterGroup: IParameterGroup;
```

- *Type:* aws-cdk-lib.aws_rds.IParameterGroup
- *Default:* no parameter group

The DB parameter group to associate with the instance.

---

##### `performanceInsightEncryptionKey`<sup>Optional</sup> <a name="performanceInsightEncryptionKey" id="eoapi-cdk.PgStacDatabaseProps.property.performanceInsightEncryptionKey"></a>

```typescript
public readonly performanceInsightEncryptionKey: IKey;
```

- *Type:* aws-cdk-lib.aws_kms.IKey
- *Default:* default master key

The AWS KMS key for encryption of Performance Insights data.

---

##### `performanceInsightRetention`<sup>Optional</sup> <a name="performanceInsightRetention" id="eoapi-cdk.PgStacDatabaseProps.property.performanceInsightRetention"></a>

```typescript
public readonly performanceInsightRetention: PerformanceInsightRetention;
```

- *Type:* aws-cdk-lib.aws_rds.PerformanceInsightRetention
- *Default:* 7 this is the free tier

The amount of time, in days, to retain Performance Insights data.

---

##### `port`<sup>Optional</sup> <a name="port" id="eoapi-cdk.PgStacDatabaseProps.property.port"></a>

```typescript
public readonly port: number;
```

- *Type:* number
- *Default:* the default port for the chosen engine.

The port for the instance.

---

##### `preferredBackupWindow`<sup>Optional</sup> <a name="preferredBackupWindow" id="eoapi-cdk.PgStacDatabaseProps.property.preferredBackupWindow"></a>

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

##### `preferredMaintenanceWindow`<sup>Optional</sup> <a name="preferredMaintenanceWindow" id="eoapi-cdk.PgStacDatabaseProps.property.preferredMaintenanceWindow"></a>

```typescript
public readonly preferredMaintenanceWindow: string;
```

- *Type:* string
- *Default:* a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#Concepts.DBMaintenance

The weekly time range (in UTC) during which system maintenance can occur.

Format: `ddd:hh24:mi-ddd:hh24:mi`
Constraint: Minimum 30-minute window

---

##### `processorFeatures`<sup>Optional</sup> <a name="processorFeatures" id="eoapi-cdk.PgStacDatabaseProps.property.processorFeatures"></a>

```typescript
public readonly processorFeatures: ProcessorFeatures;
```

- *Type:* aws-cdk-lib.aws_rds.ProcessorFeatures
- *Default:* the default number of CPU cores and threads per core for the chosen instance class.  See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor

The number of CPU cores and the number of threads per core.

---

##### `publiclyAccessible`<sup>Optional</sup> <a name="publiclyAccessible" id="eoapi-cdk.PgStacDatabaseProps.property.publiclyAccessible"></a>

```typescript
public readonly publiclyAccessible: boolean;
```

- *Type:* boolean
- *Default:* `true` if the instance's `vpcSubnets` is `subnetType: SubnetType.PUBLIC`, `false` otherwise

Indicates whether the DB instance is an internet-facing instance.

If not specified,
the instance's vpcSubnets will be used to determine if the instance is internet-facing
or not.

---

##### `removalPolicy`<sup>Optional</sup> <a name="removalPolicy" id="eoapi-cdk.PgStacDatabaseProps.property.removalPolicy"></a>

```typescript
public readonly removalPolicy: RemovalPolicy;
```

- *Type:* aws-cdk-lib.RemovalPolicy
- *Default:* RemovalPolicy.SNAPSHOT (remove the resource, but retain a snapshot of the data)

The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update.

---

##### `s3ExportBuckets`<sup>Optional</sup> <a name="s3ExportBuckets" id="eoapi-cdk.PgStacDatabaseProps.property.s3ExportBuckets"></a>

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

##### `s3ExportRole`<sup>Optional</sup> <a name="s3ExportRole" id="eoapi-cdk.PgStacDatabaseProps.property.s3ExportRole"></a>

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

##### `s3ImportBuckets`<sup>Optional</sup> <a name="s3ImportBuckets" id="eoapi-cdk.PgStacDatabaseProps.property.s3ImportBuckets"></a>

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

##### `s3ImportRole`<sup>Optional</sup> <a name="s3ImportRole" id="eoapi-cdk.PgStacDatabaseProps.property.s3ImportRole"></a>

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

##### `securityGroups`<sup>Optional</sup> <a name="securityGroups" id="eoapi-cdk.PgStacDatabaseProps.property.securityGroups"></a>

```typescript
public readonly securityGroups: ISecurityGroup[];
```

- *Type:* aws-cdk-lib.aws_ec2.ISecurityGroup[]
- *Default:* a new security group is created

The security groups to assign to the DB instance.

---

##### `storageThroughput`<sup>Optional</sup> <a name="storageThroughput" id="eoapi-cdk.PgStacDatabaseProps.property.storageThroughput"></a>

```typescript
public readonly storageThroughput: number;
```

- *Type:* number
- *Default:* 125 MiBps if allocated storage is less than 400 GiB for MariaDB, MySQL, and PostgreSQL, less than 200 GiB for Oracle and less than 20 GiB for SQL Server. 500 MiBps otherwise (except for SQL Server where the default is always 125 MiBps).

The storage throughput, specified in mebibytes per second (MiBps).

Only applicable for GP3.

> [https://docs.aws.amazon.com//AmazonRDS/latest/UserGuide/CHAP_Storage.html#gp3-storage](https://docs.aws.amazon.com//AmazonRDS/latest/UserGuide/CHAP_Storage.html#gp3-storage)

---

##### `storageType`<sup>Optional</sup> <a name="storageType" id="eoapi-cdk.PgStacDatabaseProps.property.storageType"></a>

```typescript
public readonly storageType: StorageType;
```

- *Type:* aws-cdk-lib.aws_rds.StorageType
- *Default:* GP2

The storage type.

Storage types supported are gp2, io1, standard.

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#Concepts.Storage.GeneralSSD](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#Concepts.Storage.GeneralSSD)

---

##### `subnetGroup`<sup>Optional</sup> <a name="subnetGroup" id="eoapi-cdk.PgStacDatabaseProps.property.subnetGroup"></a>

```typescript
public readonly subnetGroup: ISubnetGroup;
```

- *Type:* aws-cdk-lib.aws_rds.ISubnetGroup
- *Default:* a new subnet group will be created.

Existing subnet group for the instance.

---

##### `vpcSubnets`<sup>Optional</sup> <a name="vpcSubnets" id="eoapi-cdk.PgStacDatabaseProps.property.vpcSubnets"></a>

```typescript
public readonly vpcSubnets: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection
- *Default:* private subnets

The type of subnets to add to the created DB subnet group.

---

##### `engine`<sup>Required</sup> <a name="engine" id="eoapi-cdk.PgStacDatabaseProps.property.engine"></a>

```typescript
public readonly engine: IInstanceEngine;
```

- *Type:* aws-cdk-lib.aws_rds.IInstanceEngine

The database engine.

---

##### `allocatedStorage`<sup>Optional</sup> <a name="allocatedStorage" id="eoapi-cdk.PgStacDatabaseProps.property.allocatedStorage"></a>

```typescript
public readonly allocatedStorage: number;
```

- *Type:* number
- *Default:* 100

The allocated storage size, specified in gibibytes (GiB).

---

##### `allowMajorVersionUpgrade`<sup>Optional</sup> <a name="allowMajorVersionUpgrade" id="eoapi-cdk.PgStacDatabaseProps.property.allowMajorVersionUpgrade"></a>

```typescript
public readonly allowMajorVersionUpgrade: boolean;
```

- *Type:* boolean
- *Default:* false

Whether to allow major version upgrades.

---

##### `databaseName`<sup>Optional</sup> <a name="databaseName" id="eoapi-cdk.PgStacDatabaseProps.property.databaseName"></a>

```typescript
public readonly databaseName: string;
```

- *Type:* string
- *Default:* no name

The name of the database.

---

##### `instanceType`<sup>Optional</sup> <a name="instanceType" id="eoapi-cdk.PgStacDatabaseProps.property.instanceType"></a>

```typescript
public readonly instanceType: InstanceType;
```

- *Type:* aws-cdk-lib.aws_ec2.InstanceType
- *Default:* m5.large (or, more specifically, db.m5.large)

The name of the compute and memory capacity for the instance.

---

##### `licenseModel`<sup>Optional</sup> <a name="licenseModel" id="eoapi-cdk.PgStacDatabaseProps.property.licenseModel"></a>

```typescript
public readonly licenseModel: LicenseModel;
```

- *Type:* aws-cdk-lib.aws_rds.LicenseModel
- *Default:* RDS default license model

The license model.

---

##### `parameters`<sup>Optional</sup> <a name="parameters" id="eoapi-cdk.PgStacDatabaseProps.property.parameters"></a>

```typescript
public readonly parameters: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}
- *Default:* None

The parameters in the DBParameterGroup to create automatically.

You can only specify parameterGroup or parameters but not both.
You need to use a versioned engine to auto-generate a DBParameterGroup.

---

##### `timezone`<sup>Optional</sup> <a name="timezone" id="eoapi-cdk.PgStacDatabaseProps.property.timezone"></a>

```typescript
public readonly timezone: string;
```

- *Type:* string
- *Default:* RDS default timezone

The time zone of the instance.

This is currently supported only by Microsoft Sql Server.

---

##### `characterSetName`<sup>Optional</sup> <a name="characterSetName" id="eoapi-cdk.PgStacDatabaseProps.property.characterSetName"></a>

```typescript
public readonly characterSetName: string;
```

- *Type:* string
- *Default:* RDS default character set name

For supported engines, specifies the character set to associate with the DB instance.

---

##### `credentials`<sup>Optional</sup> <a name="credentials" id="eoapi-cdk.PgStacDatabaseProps.property.credentials"></a>

```typescript
public readonly credentials: Credentials;
```

- *Type:* aws-cdk-lib.aws_rds.Credentials
- *Default:* A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password

Credentials for the administrative user.

---

##### `storageEncrypted`<sup>Optional</sup> <a name="storageEncrypted" id="eoapi-cdk.PgStacDatabaseProps.property.storageEncrypted"></a>

```typescript
public readonly storageEncrypted: boolean;
```

- *Type:* boolean
- *Default:* true if storageEncryptionKey has been provided, false otherwise

Indicates whether the DB instance is encrypted.

---

##### `storageEncryptionKey`<sup>Optional</sup> <a name="storageEncryptionKey" id="eoapi-cdk.PgStacDatabaseProps.property.storageEncryptionKey"></a>

```typescript
public readonly storageEncryptionKey: IKey;
```

- *Type:* aws-cdk-lib.aws_kms.IKey
- *Default:* default master key if storageEncrypted is true, no key otherwise

The KMS key that's used to encrypt the DB instance.

---

##### `addPgbouncer`<sup>Optional</sup> <a name="addPgbouncer" id="eoapi-cdk.PgStacDatabaseProps.property.addPgbouncer"></a>

```typescript
public readonly addPgbouncer: boolean;
```

- *Type:* boolean
- *Default:* true

Add pgbouncer instance for managing traffic to the pgSTAC database.

---

##### `bootstrapperLambdaFunctionOptions`<sup>Optional</sup> <a name="bootstrapperLambdaFunctionOptions" id="eoapi-cdk.PgStacDatabaseProps.property.bootstrapperLambdaFunctionOptions"></a>

```typescript
public readonly bootstrapperLambdaFunctionOptions: any;
```

- *Type:* any
- *Default:* defined in the construct.

Can be used to override the default lambda function properties.

---

##### `customResourceProperties`<sup>Optional</sup> <a name="customResourceProperties" id="eoapi-cdk.PgStacDatabaseProps.property.customResourceProperties"></a>

```typescript
public readonly customResourceProperties: {[ key: string ]: any};
```

- *Type:* {[ key: string ]: any}

Lambda function Custom Resource properties.

A custom resource property is going to be created
to trigger the boostrapping lambda function. This parameter allows the user to specify additional properties
on top of the defaults ones.

---

##### `pgstacDbName`<sup>Optional</sup> <a name="pgstacDbName" id="eoapi-cdk.PgStacDatabaseProps.property.pgstacDbName"></a>

```typescript
public readonly pgstacDbName: string;
```

- *Type:* string
- *Default:* pgstac

Name of database that is to be created and onto which pgSTAC will be installed.

---

##### `pgstacUsername`<sup>Optional</sup> <a name="pgstacUsername" id="eoapi-cdk.PgStacDatabaseProps.property.pgstacUsername"></a>

```typescript
public readonly pgstacUsername: string;
```

- *Type:* string
- *Default:* pgstac_user

Name of user that will be generated for connecting to the pgSTAC database.

---

##### `pgstacVersion`<sup>Optional</sup> <a name="pgstacVersion" id="eoapi-cdk.PgStacDatabaseProps.property.pgstacVersion"></a>

```typescript
public readonly pgstacVersion: string;
```

- *Type:* string
- *Default:* 0.8.5

Version of pgstac to install on the database.

---

##### `secretsPrefix`<sup>Optional</sup> <a name="secretsPrefix" id="eoapi-cdk.PgStacDatabaseProps.property.secretsPrefix"></a>

```typescript
public readonly secretsPrefix: string;
```

- *Type:* string
- *Default:* pgstac

Prefix to assign to the generated `secrets_manager.Secret`.

---

### StacBrowserProps <a name="StacBrowserProps" id="eoapi-cdk.StacBrowserProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.StacBrowserProps.Initializer"></a>

```typescript
import { StacBrowserProps } from 'eoapi-cdk'

const stacBrowserProps: StacBrowserProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.githubRepoTag">githubRepoTag</a></code> | <code>string</code> | Tag of the radiant earth stac-browser repo to use to build the app. |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.stacCatalogUrl">stacCatalogUrl</a></code> | <code>string</code> | STAC catalog URL. |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.bucketArn">bucketArn</a></code> | <code>string</code> | Bucket ARN. |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.cloneDirectory">cloneDirectory</a></code> | <code>string</code> | Location in the filesystem where to compile the browser code. |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.cloudFrontDistributionArn">cloudFrontDistributionArn</a></code> | <code>string</code> | The ARN of the cloudfront distribution that will be added to the bucket policy with read access. |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.configFilePath">configFilePath</a></code> | <code>string</code> | Path to config file for the STAC browser. |
| <code><a href="#eoapi-cdk.StacBrowserProps.property.websiteIndexDocument">websiteIndexDocument</a></code> | <code>string</code> | The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. |

---

##### `githubRepoTag`<sup>Required</sup> <a name="githubRepoTag" id="eoapi-cdk.StacBrowserProps.property.githubRepoTag"></a>

```typescript
public readonly githubRepoTag: string;
```

- *Type:* string

Tag of the radiant earth stac-browser repo to use to build the app.

---

##### `stacCatalogUrl`<sup>Required</sup> <a name="stacCatalogUrl" id="eoapi-cdk.StacBrowserProps.property.stacCatalogUrl"></a>

```typescript
public readonly stacCatalogUrl: string;
```

- *Type:* string

STAC catalog URL.

Overrides the catalog URL in the stac-browser configuration.

---

##### `bucketArn`<sup>Optional</sup> <a name="bucketArn" id="eoapi-cdk.StacBrowserProps.property.bucketArn"></a>

```typescript
public readonly bucketArn: string;
```

- *Type:* string
- *Default:* No bucket ARN. A new bucket will be created.

Bucket ARN.

If specified, the identity used to deploy the stack must have the appropriate permissions to create a deployment for this bucket.
In addition, if specified, `cloudFrontDistributionArn` is ignored since the policy of an imported resource can't be modified.

---

##### `cloneDirectory`<sup>Optional</sup> <a name="cloneDirectory" id="eoapi-cdk.StacBrowserProps.property.cloneDirectory"></a>

```typescript
public readonly cloneDirectory: string;
```

- *Type:* string
- *Default:* DEFAULT_CLONE_DIRECTORY

Location in the filesystem where to compile the browser code.

---

##### `cloudFrontDistributionArn`<sup>Optional</sup> <a name="cloudFrontDistributionArn" id="eoapi-cdk.StacBrowserProps.property.cloudFrontDistributionArn"></a>

```typescript
public readonly cloudFrontDistributionArn: string;
```

- *Type:* string
- *Default:* No cloudfront distribution ARN. The bucket policy will not be modified.

The ARN of the cloudfront distribution that will be added to the bucket policy with read access.

If `bucketArn` is specified, this parameter is ignored since the policy of an imported bucket can't be modified.

---

##### `configFilePath`<sup>Optional</sup> <a name="configFilePath" id="eoapi-cdk.StacBrowserProps.property.configFilePath"></a>

```typescript
public readonly configFilePath: string;
```

- *Type:* string

Path to config file for the STAC browser.

If not provided, default configuration in the STAC browser
repository is used.

---

##### `websiteIndexDocument`<sup>Optional</sup> <a name="websiteIndexDocument" id="eoapi-cdk.StacBrowserProps.property.websiteIndexDocument"></a>

```typescript
public readonly websiteIndexDocument: string;
```

- *Type:* string
- *Default:* No index document.

The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket.

---

### StacIngestorProps <a name="StacIngestorProps" id="eoapi-cdk.StacIngestorProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.StacIngestorProps.Initializer"></a>

```typescript
import { StacIngestorProps } from 'eoapi-cdk'

const stacIngestorProps: StacIngestorProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.dataAccessRole">dataAccessRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | ARN of AWS Role used to validate access to S3 data. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.stacDbSecret">stacDbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing pgSTAC DB connection information. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.stacDbSecurityGroup">stacDbSecurityGroup</a></code> | <code>aws-cdk-lib.aws_ec2.ISecurityGroup</code> | Security Group used by pgSTAC DB. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.stacUrl">stacUrl</a></code> | <code>string</code> | URL of STAC API. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.stage">stage</a></code> | <code>string</code> | Stage of deployment (e.g. `dev`, `prod`). |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.apiEndpointConfiguration">apiEndpointConfiguration</a></code> | <code>aws-cdk-lib.aws_apigateway.EndpointConfiguration</code> | API Endpoint Configuration, useful for creating private APIs. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Environment variables to be sent to Lambda. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.apiLambdaFunctionOptions">apiLambdaFunctionOptions</a></code> | <code>any</code> | Can be used to override the default lambda function properties. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.apiPolicy">apiPolicy</a></code> | <code>aws-cdk-lib.aws_iam.PolicyDocument</code> | API Policy Document, useful for creating private APIs. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.ingestorDomainNameOptions">ingestorDomainNameOptions</a></code> | <code>aws-cdk-lib.aws_apigateway.DomainNameOptions</code> | Custom Domain Name Options for Ingestor API. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.ingestorLambdaFunctionOptions">ingestorLambdaFunctionOptions</a></code> | <code>any</code> | Can be used to override the default lambda function properties. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Subnet into which the lambda should be deployed if using a VPC. |
| <code><a href="#eoapi-cdk.StacIngestorProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC running pgSTAC DB. |

---

##### `dataAccessRole`<sup>Required</sup> <a name="dataAccessRole" id="eoapi-cdk.StacIngestorProps.property.dataAccessRole"></a>

```typescript
public readonly dataAccessRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole

ARN of AWS Role used to validate access to S3 data.

---

##### `stacDbSecret`<sup>Required</sup> <a name="stacDbSecret" id="eoapi-cdk.StacIngestorProps.property.stacDbSecret"></a>

```typescript
public readonly stacDbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing pgSTAC DB connection information.

---

##### `stacDbSecurityGroup`<sup>Required</sup> <a name="stacDbSecurityGroup" id="eoapi-cdk.StacIngestorProps.property.stacDbSecurityGroup"></a>

```typescript
public readonly stacDbSecurityGroup: ISecurityGroup;
```

- *Type:* aws-cdk-lib.aws_ec2.ISecurityGroup

Security Group used by pgSTAC DB.

---

##### `stacUrl`<sup>Required</sup> <a name="stacUrl" id="eoapi-cdk.StacIngestorProps.property.stacUrl"></a>

```typescript
public readonly stacUrl: string;
```

- *Type:* string

URL of STAC API.

---

##### `stage`<sup>Required</sup> <a name="stage" id="eoapi-cdk.StacIngestorProps.property.stage"></a>

```typescript
public readonly stage: string;
```

- *Type:* string

Stage of deployment (e.g. `dev`, `prod`).

---

##### `apiEndpointConfiguration`<sup>Optional</sup> <a name="apiEndpointConfiguration" id="eoapi-cdk.StacIngestorProps.property.apiEndpointConfiguration"></a>

```typescript
public readonly apiEndpointConfiguration: EndpointConfiguration;
```

- *Type:* aws-cdk-lib.aws_apigateway.EndpointConfiguration

API Endpoint Configuration, useful for creating private APIs.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="eoapi-cdk.StacIngestorProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Environment variables to be sent to Lambda.

---

##### `apiLambdaFunctionOptions`<sup>Optional</sup> <a name="apiLambdaFunctionOptions" id="eoapi-cdk.StacIngestorProps.property.apiLambdaFunctionOptions"></a>

```typescript
public readonly apiLambdaFunctionOptions: any;
```

- *Type:* any
- *Default:* default settings are defined in the construct.

Can be used to override the default lambda function properties.

---

##### `apiPolicy`<sup>Optional</sup> <a name="apiPolicy" id="eoapi-cdk.StacIngestorProps.property.apiPolicy"></a>

```typescript
public readonly apiPolicy: PolicyDocument;
```

- *Type:* aws-cdk-lib.aws_iam.PolicyDocument

API Policy Document, useful for creating private APIs.

---

##### `ingestorDomainNameOptions`<sup>Optional</sup> <a name="ingestorDomainNameOptions" id="eoapi-cdk.StacIngestorProps.property.ingestorDomainNameOptions"></a>

```typescript
public readonly ingestorDomainNameOptions: DomainNameOptions;
```

- *Type:* aws-cdk-lib.aws_apigateway.DomainNameOptions

Custom Domain Name Options for Ingestor API.

---

##### `ingestorLambdaFunctionOptions`<sup>Optional</sup> <a name="ingestorLambdaFunctionOptions" id="eoapi-cdk.StacIngestorProps.property.ingestorLambdaFunctionOptions"></a>

```typescript
public readonly ingestorLambdaFunctionOptions: any;
```

- *Type:* any
- *Default:* default settings are defined in the construct.

Can be used to override the default lambda function properties.

---

##### `subnetSelection`<sup>Optional</sup> <a name="subnetSelection" id="eoapi-cdk.StacIngestorProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Subnet into which the lambda should be deployed if using a VPC.

---

##### `vpc`<sup>Optional</sup> <a name="vpc" id="eoapi-cdk.StacIngestorProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC running pgSTAC DB.

---

### TiPgApiLambdaProps <a name="TiPgApiLambdaProps" id="eoapi-cdk.TiPgApiLambdaProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.TiPgApiLambdaProps.Initializer"></a>

```typescript
import { TiPgApiLambdaProps } from 'eoapi-cdk'

const tiPgApiLambdaProps: TiPgApiLambdaProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance \| aws-cdk-lib.aws_ec2.IInstance</code> | RDS Instance with installed pgSTAC or pgbouncer server. |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing connection information for pgSTAC database. |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Customized environment variables to send to titiler-pgstac runtime. |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.lambdaFunctionOptions">lambdaFunctionOptions</a></code> | <code>any</code> | Can be used to override the default lambda function properties. |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Subnet into which the lambda should be deployed. |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.tipgApiDomainName">tipgApiDomainName</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.IDomainName</code> | Custom Domain Name for tipg API. |
| <code><a href="#eoapi-cdk.TiPgApiLambdaProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC into which the lambda should be deployed. |

---

##### `db`<sup>Required</sup> <a name="db" id="eoapi-cdk.TiPgApiLambdaProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance | IInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance | aws-cdk-lib.aws_ec2.IInstance

RDS Instance with installed pgSTAC or pgbouncer server.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="eoapi-cdk.TiPgApiLambdaProps.property.dbSecret"></a>

```typescript
public readonly dbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing connection information for pgSTAC database.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="eoapi-cdk.TiPgApiLambdaProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Customized environment variables to send to titiler-pgstac runtime.

---

##### `lambdaFunctionOptions`<sup>Optional</sup> <a name="lambdaFunctionOptions" id="eoapi-cdk.TiPgApiLambdaProps.property.lambdaFunctionOptions"></a>

```typescript
public readonly lambdaFunctionOptions: any;
```

- *Type:* any
- *Default:* defined in the construct.

Can be used to override the default lambda function properties.

---

##### `subnetSelection`<sup>Optional</sup> <a name="subnetSelection" id="eoapi-cdk.TiPgApiLambdaProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Subnet into which the lambda should be deployed.

---

##### `tipgApiDomainName`<sup>Optional</sup> <a name="tipgApiDomainName" id="eoapi-cdk.TiPgApiLambdaProps.property.tipgApiDomainName"></a>

```typescript
public readonly tipgApiDomainName: IDomainName;
```

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.IDomainName
- *Default:* undefined

Custom Domain Name for tipg API.

If defined, will create the
domain name and integrate it with the tipg API.

---

##### `vpc`<sup>Optional</sup> <a name="vpc" id="eoapi-cdk.TiPgApiLambdaProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC into which the lambda should be deployed.

---

### TitilerPgStacApiLambdaProps <a name="TitilerPgStacApiLambdaProps" id="eoapi-cdk.TitilerPgStacApiLambdaProps"></a>

#### Initializer <a name="Initializer" id="eoapi-cdk.TitilerPgStacApiLambdaProps.Initializer"></a>

```typescript
import { TitilerPgStacApiLambdaProps } from 'eoapi-cdk'

const titilerPgStacApiLambdaProps: TitilerPgStacApiLambdaProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance \| aws-cdk-lib.aws_ec2.IInstance</code> | RDS Instance with installed pgSTAC or pgbouncer server. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing connection information for pgSTAC database. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Customized environment variables to send to titiler-pgstac runtime. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.buckets">buckets</a></code> | <code>string[]</code> | list of buckets the lambda will be granted access to. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.lambdaFunctionOptions">lambdaFunctionOptions</a></code> | <code>any</code> | Can be used to override the default lambda function properties. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Subnet into which the lambda should be deployed. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.titilerPgstacApiDomainName">titilerPgstacApiDomainName</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.IDomainName</code> | Custom Domain Name Options for Titiler Pgstac API,. |
| <code><a href="#eoapi-cdk.TitilerPgStacApiLambdaProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC into which the lambda should be deployed. |

---

##### `db`<sup>Required</sup> <a name="db" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance | IInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance | aws-cdk-lib.aws_ec2.IInstance

RDS Instance with installed pgSTAC or pgbouncer server.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.dbSecret"></a>

```typescript
public readonly dbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing connection information for pgSTAC database.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Customized environment variables to send to titiler-pgstac runtime.

These will be merged with `defaultTitilerPgstacEnv`.
The database secret arn is automatically added to the environment variables at deployment.
/

---

##### `buckets`<sup>Optional</sup> <a name="buckets" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.buckets"></a>

```typescript
public readonly buckets: string[];
```

- *Type:* string[]

list of buckets the lambda will be granted access to.

---

##### `lambdaFunctionOptions`<sup>Optional</sup> <a name="lambdaFunctionOptions" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.lambdaFunctionOptions"></a>

```typescript
public readonly lambdaFunctionOptions: any;
```

- *Type:* any
- *Default:* defined in the construct.

Can be used to override the default lambda function properties.

---

##### `subnetSelection`<sup>Optional</sup> <a name="subnetSelection" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Subnet into which the lambda should be deployed.

---

##### `titilerPgstacApiDomainName`<sup>Optional</sup> <a name="titilerPgstacApiDomainName" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.titilerPgstacApiDomainName"></a>

```typescript
public readonly titilerPgstacApiDomainName: IDomainName;
```

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.IDomainName
- *Default:* undefined.

Custom Domain Name Options for Titiler Pgstac API,.

---

##### `vpc`<sup>Optional</sup> <a name="vpc" id="eoapi-cdk.TitilerPgStacApiLambdaProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC into which the lambda should be deployed.

---



