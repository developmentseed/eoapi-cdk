# API Reference <a name="API Reference" id="api-reference"></a>

## Constructs <a name="Constructs" id="Constructs"></a>

### BastionHost <a name="BastionHost" id="cdk-pgstac.BastionHost"></a>

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

#### Initializers <a name="Initializers" id="cdk-pgstac.BastionHost.Initializer"></a>

```typescript
import { BastionHost } from 'cdk-pgstac'

new BastionHost(scope: Construct, id: string, props: BastionHostProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.BastionHost.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#cdk-pgstac.BastionHost.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.BastionHost.Initializer.parameter.props">props</a></code> | <code><a href="#cdk-pgstac.BastionHostProps">BastionHostProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="cdk-pgstac.BastionHost.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="cdk-pgstac.BastionHost.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="cdk-pgstac.BastionHost.Initializer.parameter.props"></a>

- *Type:* <a href="#cdk-pgstac.BastionHostProps">BastionHostProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.BastionHost.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="cdk-pgstac.BastionHost.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.BastionHost.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="cdk-pgstac.BastionHost.isConstruct"></a>

```typescript
import { BastionHost } from 'cdk-pgstac'

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

###### `x`<sup>Required</sup> <a name="x" id="cdk-pgstac.BastionHost.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.BastionHost.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#cdk-pgstac.BastionHost.property.instance">instance</a></code> | <code>aws-cdk-lib.aws_ec2.Instance</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="cdk-pgstac.BastionHost.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `instance`<sup>Required</sup> <a name="instance" id="cdk-pgstac.BastionHost.property.instance"></a>

```typescript
public readonly instance: Instance;
```

- *Type:* aws-cdk-lib.aws_ec2.Instance

---


### BootstrapPgStac <a name="BootstrapPgStac" id="cdk-pgstac.BootstrapPgStac"></a>

Bootstraps a database instance, installing pgSTAC onto the database.

#### Initializers <a name="Initializers" id="cdk-pgstac.BootstrapPgStac.Initializer"></a>

```typescript
import { BootstrapPgStac } from 'cdk-pgstac'

new BootstrapPgStac(scope: Construct, id: string, props: BootstrapPgStacProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.BootstrapPgStac.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#cdk-pgstac.BootstrapPgStac.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.BootstrapPgStac.Initializer.parameter.props">props</a></code> | <code><a href="#cdk-pgstac.BootstrapPgStacProps">BootstrapPgStacProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="cdk-pgstac.BootstrapPgStac.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="cdk-pgstac.BootstrapPgStac.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="cdk-pgstac.BootstrapPgStac.Initializer.parameter.props"></a>

- *Type:* <a href="#cdk-pgstac.BootstrapPgStacProps">BootstrapPgStacProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.BootstrapPgStac.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="cdk-pgstac.BootstrapPgStac.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.BootstrapPgStac.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="cdk-pgstac.BootstrapPgStac.isConstruct"></a>

```typescript
import { BootstrapPgStac } from 'cdk-pgstac'

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

###### `x`<sup>Required</sup> <a name="x" id="cdk-pgstac.BootstrapPgStac.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.BootstrapPgStac.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#cdk-pgstac.BootstrapPgStac.property.secret">secret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="cdk-pgstac.BootstrapPgStac.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `secret`<sup>Required</sup> <a name="secret" id="cdk-pgstac.BootstrapPgStac.property.secret"></a>

```typescript
public readonly secret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

---


### PgStacApiLambda <a name="PgStacApiLambda" id="cdk-pgstac.PgStacApiLambda"></a>

#### Initializers <a name="Initializers" id="cdk-pgstac.PgStacApiLambda.Initializer"></a>

```typescript
import { PgStacApiLambda } from 'cdk-pgstac'

new PgStacApiLambda(scope: Construct, id: string, props: PgStacApiLambdaProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.PgStacApiLambda.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacApiLambda.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacApiLambda.Initializer.parameter.props">props</a></code> | <code><a href="#cdk-pgstac.PgStacApiLambdaProps">PgStacApiLambdaProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="cdk-pgstac.PgStacApiLambda.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="cdk-pgstac.PgStacApiLambda.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="cdk-pgstac.PgStacApiLambda.Initializer.parameter.props"></a>

- *Type:* <a href="#cdk-pgstac.PgStacApiLambdaProps">PgStacApiLambdaProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.PgStacApiLambda.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="cdk-pgstac.PgStacApiLambda.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.PgStacApiLambda.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="cdk-pgstac.PgStacApiLambda.isConstruct"></a>

```typescript
import { PgStacApiLambda } from 'cdk-pgstac'

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

###### `x`<sup>Required</sup> <a name="x" id="cdk-pgstac.PgStacApiLambda.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.PgStacApiLambda.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#cdk-pgstac.PgStacApiLambda.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacApiLambda.property.stacApiLambdaFunction">stacApiLambdaFunction</a></code> | <code>@aws-cdk/aws-lambda-python-alpha.PythonFunction</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="cdk-pgstac.PgStacApiLambda.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `url`<sup>Required</sup> <a name="url" id="cdk-pgstac.PgStacApiLambda.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `stacApiLambdaFunction`<sup>Required</sup> <a name="stacApiLambdaFunction" id="cdk-pgstac.PgStacApiLambda.property.stacApiLambdaFunction"></a>

```typescript
public readonly stacApiLambdaFunction: PythonFunction;
```

- *Type:* @aws-cdk/aws-lambda-python-alpha.PythonFunction

---


### PgStacDatabase <a name="PgStacDatabase" id="cdk-pgstac.PgStacDatabase"></a>

An RDS instance with pgSTAC installed.

This is a wrapper around the
`rds.DatabaseInstance` higher-level construct making use
of the BootstrapPgStac construct.

#### Initializers <a name="Initializers" id="cdk-pgstac.PgStacDatabase.Initializer"></a>

```typescript
import { PgStacDatabase } from 'cdk-pgstac'

new PgStacDatabase(scope: Construct, id: string, props: PgStacDatabaseProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.PgStacDatabase.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacDatabase.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacDatabase.Initializer.parameter.props">props</a></code> | <code><a href="#cdk-pgstac.PgStacDatabaseProps">PgStacDatabaseProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="cdk-pgstac.PgStacDatabase.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="cdk-pgstac.PgStacDatabase.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="cdk-pgstac.PgStacDatabase.Initializer.parameter.props"></a>

- *Type:* <a href="#cdk-pgstac.PgStacDatabaseProps">PgStacDatabaseProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.PgStacDatabase.toString">toString</a></code> | Returns a string representation of this construct. |
| <code><a href="#cdk-pgstac.PgStacDatabase.getParameters">getParameters</a></code> | *No description.* |

---

##### `toString` <a name="toString" id="cdk-pgstac.PgStacDatabase.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

##### `getParameters` <a name="getParameters" id="cdk-pgstac.PgStacDatabase.getParameters"></a>

```typescript
public getParameters(instanceType: string, parameters?: {[ key: string ]: string}): DatabaseParameters
```

###### `instanceType`<sup>Required</sup> <a name="instanceType" id="cdk-pgstac.PgStacDatabase.getParameters.parameter.instanceType"></a>

- *Type:* string

---

###### `parameters`<sup>Optional</sup> <a name="parameters" id="cdk-pgstac.PgStacDatabase.getParameters.parameter.parameters"></a>

- *Type:* {[ key: string ]: string}

---

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.PgStacDatabase.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="cdk-pgstac.PgStacDatabase.isConstruct"></a>

```typescript
import { PgStacDatabase } from 'cdk-pgstac'

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

###### `x`<sup>Required</sup> <a name="x" id="cdk-pgstac.PgStacDatabase.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.PgStacDatabase.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#cdk-pgstac.PgStacDatabase.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.DatabaseInstance</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacDatabase.property.pgstacSecret">pgstacSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="cdk-pgstac.PgStacDatabase.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `db`<sup>Required</sup> <a name="db" id="cdk-pgstac.PgStacDatabase.property.db"></a>

```typescript
public readonly db: DatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.DatabaseInstance

---

##### `pgstacSecret`<sup>Required</sup> <a name="pgstacSecret" id="cdk-pgstac.PgStacDatabase.property.pgstacSecret"></a>

```typescript
public readonly pgstacSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

---


### StacIngestor <a name="StacIngestor" id="cdk-pgstac.StacIngestor"></a>

#### Initializers <a name="Initializers" id="cdk-pgstac.StacIngestor.Initializer"></a>

```typescript
import { StacIngestor } from 'cdk-pgstac'

new StacIngestor(scope: Construct, id: string, props: StacIngestorProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.StacIngestor.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#cdk-pgstac.StacIngestor.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.StacIngestor.Initializer.parameter.props">props</a></code> | <code><a href="#cdk-pgstac.StacIngestorProps">StacIngestorProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="cdk-pgstac.StacIngestor.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="cdk-pgstac.StacIngestor.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="cdk-pgstac.StacIngestor.Initializer.parameter.props"></a>

- *Type:* <a href="#cdk-pgstac.StacIngestorProps">StacIngestorProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.StacIngestor.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="cdk-pgstac.StacIngestor.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.StacIngestor.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="cdk-pgstac.StacIngestor.isConstruct"></a>

```typescript
import { StacIngestor } from 'cdk-pgstac'

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

###### `x`<sup>Required</sup> <a name="x" id="cdk-pgstac.StacIngestor.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.StacIngestor.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#cdk-pgstac.StacIngestor.property.handlerRole">handlerRole</a></code> | <code>aws-cdk-lib.aws_iam.Role</code> | *No description.* |
| <code><a href="#cdk-pgstac.StacIngestor.property.table">table</a></code> | <code>aws-cdk-lib.aws_dynamodb.Table</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="cdk-pgstac.StacIngestor.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `handlerRole`<sup>Required</sup> <a name="handlerRole" id="cdk-pgstac.StacIngestor.property.handlerRole"></a>

```typescript
public readonly handlerRole: Role;
```

- *Type:* aws-cdk-lib.aws_iam.Role

---

##### `table`<sup>Required</sup> <a name="table" id="cdk-pgstac.StacIngestor.property.table"></a>

```typescript
public readonly table: Table;
```

- *Type:* aws-cdk-lib.aws_dynamodb.Table

---


### TitilerPgstacApiLambda <a name="TitilerPgstacApiLambda" id="cdk-pgstac.TitilerPgstacApiLambda"></a>

#### Initializers <a name="Initializers" id="cdk-pgstac.TitilerPgstacApiLambda.Initializer"></a>

```typescript
import { TitilerPgstacApiLambda } from 'cdk-pgstac'

new TitilerPgstacApiLambda(scope: Construct, id: string, props: TitilerPgStacApiLambdaProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.Initializer.parameter.props">props</a></code> | <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps">TitilerPgStacApiLambdaProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="cdk-pgstac.TitilerPgstacApiLambda.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="cdk-pgstac.TitilerPgstacApiLambda.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="cdk-pgstac.TitilerPgstacApiLambda.Initializer.parameter.props"></a>

- *Type:* <a href="#cdk-pgstac.TitilerPgStacApiLambdaProps">TitilerPgStacApiLambdaProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="cdk-pgstac.TitilerPgstacApiLambda.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### `isConstruct` <a name="isConstruct" id="cdk-pgstac.TitilerPgstacApiLambda.isConstruct"></a>

```typescript
import { TitilerPgstacApiLambda } from 'cdk-pgstac'

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

###### `x`<sup>Required</sup> <a name="x" id="cdk-pgstac.TitilerPgstacApiLambda.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.TitilerPgstacApiLambda.property.titilerPgstacLambdaFunction">titilerPgstacLambdaFunction</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="cdk-pgstac.TitilerPgstacApiLambda.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `url`<sup>Required</sup> <a name="url" id="cdk-pgstac.TitilerPgstacApiLambda.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `titilerPgstacLambdaFunction`<sup>Required</sup> <a name="titilerPgstacLambdaFunction" id="cdk-pgstac.TitilerPgstacApiLambda.property.titilerPgstacLambdaFunction"></a>

```typescript
public readonly titilerPgstacLambdaFunction: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---


## Structs <a name="Structs" id="Structs"></a>

### ApiEntrypoint <a name="ApiEntrypoint" id="cdk-pgstac.ApiEntrypoint"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.ApiEntrypoint.Initializer"></a>

```typescript
import { ApiEntrypoint } from 'cdk-pgstac'

const apiEntrypoint: ApiEntrypoint = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.ApiEntrypoint.property.entry">entry</a></code> | <code>string</code> | Path to the source of the function or the location for dependencies. |
| <code><a href="#cdk-pgstac.ApiEntrypoint.property.handler">handler</a></code> | <code>string</code> | The name of the exported handler in the index file. |
| <code><a href="#cdk-pgstac.ApiEntrypoint.property.index">index</a></code> | <code>string</code> | The path (relative to entry) to the index file containing the exported handler. |

---

##### `entry`<sup>Required</sup> <a name="entry" id="cdk-pgstac.ApiEntrypoint.property.entry"></a>

```typescript
public readonly entry: string;
```

- *Type:* string

Path to the source of the function or the location for dependencies.

---

##### `handler`<sup>Optional</sup> <a name="handler" id="cdk-pgstac.ApiEntrypoint.property.handler"></a>

```typescript
public readonly handler: string;
```

- *Type:* string

The name of the exported handler in the index file.

---

##### `index`<sup>Optional</sup> <a name="index" id="cdk-pgstac.ApiEntrypoint.property.index"></a>

```typescript
public readonly index: string;
```

- *Type:* string

The path (relative to entry) to the index file containing the exported handler.

---

### BastionHostProps <a name="BastionHostProps" id="cdk-pgstac.BastionHostProps"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.BastionHostProps.Initializer"></a>

```typescript
import { BastionHostProps } from 'cdk-pgstac'

const bastionHostProps: BastionHostProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.BastionHostProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance</code> | *No description.* |
| <code><a href="#cdk-pgstac.BastionHostProps.property.ipv4Allowlist">ipv4Allowlist</a></code> | <code>string[]</code> | *No description.* |
| <code><a href="#cdk-pgstac.BastionHostProps.property.userData">userData</a></code> | <code>aws-cdk-lib.aws_ec2.UserData</code> | *No description.* |
| <code><a href="#cdk-pgstac.BastionHostProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | *No description.* |
| <code><a href="#cdk-pgstac.BastionHostProps.property.createElasticIp">createElasticIp</a></code> | <code>boolean</code> | Whether or not an elastic IP should be created for the bastion host. |
| <code><a href="#cdk-pgstac.BastionHostProps.property.sshPort">sshPort</a></code> | <code>number</code> | *No description.* |

---

##### `db`<sup>Required</sup> <a name="db" id="cdk-pgstac.BastionHostProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance

---

##### `ipv4Allowlist`<sup>Required</sup> <a name="ipv4Allowlist" id="cdk-pgstac.BastionHostProps.property.ipv4Allowlist"></a>

```typescript
public readonly ipv4Allowlist: string[];
```

- *Type:* string[]

---

##### `userData`<sup>Required</sup> <a name="userData" id="cdk-pgstac.BastionHostProps.property.userData"></a>

```typescript
public readonly userData: UserData;
```

- *Type:* aws-cdk-lib.aws_ec2.UserData

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="cdk-pgstac.BastionHostProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

---

##### `createElasticIp`<sup>Optional</sup> <a name="createElasticIp" id="cdk-pgstac.BastionHostProps.property.createElasticIp"></a>

```typescript
public readonly createElasticIp: boolean;
```

- *Type:* boolean
- *Default:* false

Whether or not an elastic IP should be created for the bastion host.

---

##### `sshPort`<sup>Optional</sup> <a name="sshPort" id="cdk-pgstac.BastionHostProps.property.sshPort"></a>

```typescript
public readonly sshPort: number;
```

- *Type:* number

---

### BootstrapPgStacProps <a name="BootstrapPgStacProps" id="cdk-pgstac.BootstrapPgStacProps"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.BootstrapPgStacProps.Initializer"></a>

```typescript
import { BootstrapPgStacProps } from 'cdk-pgstac'

const bootstrapPgStacProps: BootstrapPgStacProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.database">database</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance \| aws-cdk-lib.aws_rds.DatabaseInstance</code> | Database onto which pgSTAC should be installed. |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing valid connection details for the database instance. |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.pgstacDbName">pgstacDbName</a></code> | <code>string</code> | Name of database that is to be created and onto which pgSTAC will be installed. |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.pgstacUsername">pgstacUsername</a></code> | <code>string</code> | Name of user that will be generated for connecting to the pgSTAC database. |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.pgstacVersion">pgstacVersion</a></code> | <code>string</code> | pgSTAC version to be installed. |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.secretsPrefix">secretsPrefix</a></code> | <code>string</code> | Prefix to assign to the generated `secrets_manager.Secret`. |
| <code><a href="#cdk-pgstac.BootstrapPgStacProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC in which the database resides. |

---

##### `database`<sup>Required</sup> <a name="database" id="cdk-pgstac.BootstrapPgStacProps.property.database"></a>

```typescript
public readonly database: IDatabaseInstance | DatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance | aws-cdk-lib.aws_rds.DatabaseInstance

Database onto which pgSTAC should be installed.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="cdk-pgstac.BootstrapPgStacProps.property.dbSecret"></a>

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

##### `pgstacDbName`<sup>Optional</sup> <a name="pgstacDbName" id="cdk-pgstac.BootstrapPgStacProps.property.pgstacDbName"></a>

```typescript
public readonly pgstacDbName: string;
```

- *Type:* string
- *Default:* pgstac

Name of database that is to be created and onto which pgSTAC will be installed.

---

##### `pgstacUsername`<sup>Optional</sup> <a name="pgstacUsername" id="cdk-pgstac.BootstrapPgStacProps.property.pgstacUsername"></a>

```typescript
public readonly pgstacUsername: string;
```

- *Type:* string
- *Default:* pgstac_user

Name of user that will be generated for connecting to the pgSTAC database.

---

##### `pgstacVersion`<sup>Optional</sup> <a name="pgstacVersion" id="cdk-pgstac.BootstrapPgStacProps.property.pgstacVersion"></a>

```typescript
public readonly pgstacVersion: string;
```

- *Type:* string
- *Default:* 0.6.8

pgSTAC version to be installed.

---

##### `secretsPrefix`<sup>Optional</sup> <a name="secretsPrefix" id="cdk-pgstac.BootstrapPgStacProps.property.secretsPrefix"></a>

```typescript
public readonly secretsPrefix: string;
```

- *Type:* string
- *Default:* pgstac

Prefix to assign to the generated `secrets_manager.Secret`.

---

##### `vpc`<sup>Optional</sup> <a name="vpc" id="cdk-pgstac.BootstrapPgStacProps.property.vpc"></a>

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

### DatabaseParameters <a name="DatabaseParameters" id="cdk-pgstac.DatabaseParameters"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.DatabaseParameters.Initializer"></a>

```typescript
import { DatabaseParameters } from 'cdk-pgstac'

const databaseParameters: DatabaseParameters = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.effectiveCacheSize">effectiveCacheSize</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.maintenanceWorkMem">maintenanceWorkMem</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.maxConnections">maxConnections</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.maxLocksPerTransaction">maxLocksPerTransaction</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.randomPageCost">randomPageCost</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.seqPageCost">seqPageCost</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.sharedBuffers">sharedBuffers</a></code> | <code>string</code> | Note: This value is measured in 8KB blocks. |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.tempBuffers">tempBuffers</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.DatabaseParameters.property.workMem">workMem</a></code> | <code>string</code> | *No description.* |

---

##### `effectiveCacheSize`<sup>Required</sup> <a name="effectiveCacheSize" id="cdk-pgstac.DatabaseParameters.property.effectiveCacheSize"></a>

```typescript
public readonly effectiveCacheSize: string;
```

- *Type:* string
- *Default:* 75% of instance memory

---

##### `maintenanceWorkMem`<sup>Required</sup> <a name="maintenanceWorkMem" id="cdk-pgstac.DatabaseParameters.property.maintenanceWorkMem"></a>

```typescript
public readonly maintenanceWorkMem: string;
```

- *Type:* string
- *Default:* 25% of shared buffers

---

##### `maxConnections`<sup>Required</sup> <a name="maxConnections" id="cdk-pgstac.DatabaseParameters.property.maxConnections"></a>

```typescript
public readonly maxConnections: string;
```

- *Type:* string
- *Default:* LEAST({DBInstanceClassMemory/9531392}, 5000)

---

##### `maxLocksPerTransaction`<sup>Required</sup> <a name="maxLocksPerTransaction" id="cdk-pgstac.DatabaseParameters.property.maxLocksPerTransaction"></a>

```typescript
public readonly maxLocksPerTransaction: string;
```

- *Type:* string
- *Default:* 1024

---

##### `randomPageCost`<sup>Required</sup> <a name="randomPageCost" id="cdk-pgstac.DatabaseParameters.property.randomPageCost"></a>

```typescript
public readonly randomPageCost: string;
```

- *Type:* string
- *Default:* 1.1

---

##### `seqPageCost`<sup>Required</sup> <a name="seqPageCost" id="cdk-pgstac.DatabaseParameters.property.seqPageCost"></a>

```typescript
public readonly seqPageCost: string;
```

- *Type:* string
- *Default:* 1

---

##### `sharedBuffers`<sup>Required</sup> <a name="sharedBuffers" id="cdk-pgstac.DatabaseParameters.property.sharedBuffers"></a>

```typescript
public readonly sharedBuffers: string;
```

- *Type:* string
- *Default:* '{DBInstanceClassMemory/32768}' 25% of instance memory, ie `{(DBInstanceClassMemory/(1024*8)) * 0.25}`

Note: This value is measured in 8KB blocks.

---

##### `tempBuffers`<sup>Required</sup> <a name="tempBuffers" id="cdk-pgstac.DatabaseParameters.property.tempBuffers"></a>

```typescript
public readonly tempBuffers: string;
```

- *Type:* string
- *Default:* 131172 (128 * 1024)

---

##### `workMem`<sup>Required</sup> <a name="workMem" id="cdk-pgstac.DatabaseParameters.property.workMem"></a>

```typescript
public readonly workMem: string;
```

- *Type:* string
- *Default:* shared buffers divided by max connections

---

### PgStacApiLambdaProps <a name="PgStacApiLambdaProps" id="cdk-pgstac.PgStacApiLambdaProps"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.PgStacApiLambdaProps.Initializer"></a>

```typescript
import { PgStacApiLambdaProps } from 'cdk-pgstac'

const pgStacApiLambdaProps: PgStacApiLambdaProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.PgStacApiLambdaProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance</code> | RDS Instance with installed pgSTAC. |
| <code><a href="#cdk-pgstac.PgStacApiLambdaProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing connection information for pgSTAC database. |
| <code><a href="#cdk-pgstac.PgStacApiLambdaProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Subnet into which the lambda should be deployed. |
| <code><a href="#cdk-pgstac.PgStacApiLambdaProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC into which the lambda should be deployed. |
| <code><a href="#cdk-pgstac.PgStacApiLambdaProps.property.apiCode">apiCode</a></code> | <code><a href="#cdk-pgstac.ApiEntrypoint">ApiEntrypoint</a></code> | Custom code to run for fastapi-pgstac. |
| <code><a href="#cdk-pgstac.PgStacApiLambdaProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Customized environment variables to send to fastapi-pgstac runtime. |

---

##### `db`<sup>Required</sup> <a name="db" id="cdk-pgstac.PgStacApiLambdaProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance

RDS Instance with installed pgSTAC.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="cdk-pgstac.PgStacApiLambdaProps.property.dbSecret"></a>

```typescript
public readonly dbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing connection information for pgSTAC database.

---

##### `subnetSelection`<sup>Required</sup> <a name="subnetSelection" id="cdk-pgstac.PgStacApiLambdaProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Subnet into which the lambda should be deployed.

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="cdk-pgstac.PgStacApiLambdaProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC into which the lambda should be deployed.

---

##### `apiCode`<sup>Optional</sup> <a name="apiCode" id="cdk-pgstac.PgStacApiLambdaProps.property.apiCode"></a>

```typescript
public readonly apiCode: ApiEntrypoint;
```

- *Type:* <a href="#cdk-pgstac.ApiEntrypoint">ApiEntrypoint</a>
- *Default:* simplified version of fastapi-pgstac

Custom code to run for fastapi-pgstac.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="cdk-pgstac.PgStacApiLambdaProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Customized environment variables to send to fastapi-pgstac runtime.

---

### PgStacDatabaseProps <a name="PgStacDatabaseProps" id="cdk-pgstac.PgStacDatabaseProps"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.PgStacDatabaseProps.Initializer"></a>

```typescript
import { PgStacDatabaseProps } from 'cdk-pgstac'

const pgStacDatabaseProps: PgStacDatabaseProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | The VPC network where the DB subnet group should be created. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.autoMinorVersionUpgrade">autoMinorVersionUpgrade</a></code> | <code>boolean</code> | Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.availabilityZone">availabilityZone</a></code> | <code>string</code> | The name of the Availability Zone where the DB instance will be located. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.backupRetention">backupRetention</a></code> | <code>aws-cdk-lib.Duration</code> | The number of days during which automatic DB snapshots are retained. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.cloudwatchLogsExports">cloudwatchLogsExports</a></code> | <code>string[]</code> | The list of log types that need to be enabled for exporting to CloudWatch Logs. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.cloudwatchLogsRetention">cloudwatchLogsRetention</a></code> | <code>aws-cdk-lib.aws_logs.RetentionDays</code> | The number of days log events are kept in CloudWatch Logs. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.cloudwatchLogsRetentionRole">cloudwatchLogsRetentionRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | The IAM role for the Lambda function associated with the custom resource that sets the retention policy. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.copyTagsToSnapshot">copyTagsToSnapshot</a></code> | <code>boolean</code> | Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.deleteAutomatedBackups">deleteAutomatedBackups</a></code> | <code>boolean</code> | Indicates whether automated backups should be deleted or retained when you delete a DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.deletionProtection">deletionProtection</a></code> | <code>boolean</code> | Indicates whether the DB instance should have deletion protection enabled. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.domain">domain</a></code> | <code>string</code> | The Active Directory directory ID to create the DB instance in. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.domainRole">domainRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | The IAM role to be used when making API calls to the Directory Service. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.enablePerformanceInsights">enablePerformanceInsights</a></code> | <code>boolean</code> | Whether to enable Performance Insights for the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.iamAuthentication">iamAuthentication</a></code> | <code>boolean</code> | Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.instanceIdentifier">instanceIdentifier</a></code> | <code>string</code> | A name for the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.iops">iops</a></code> | <code>number</code> | The number of I/O operations per second (IOPS) that the database provisions. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.maxAllocatedStorage">maxAllocatedStorage</a></code> | <code>number</code> | Upper limit to which RDS can scale the storage in GiB(Gibibyte). |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.monitoringInterval">monitoringInterval</a></code> | <code>aws-cdk-lib.Duration</code> | The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.monitoringRole">monitoringRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be used to manage DB instance monitoring. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.multiAz">multiAz</a></code> | <code>boolean</code> | Specifies if the database instance is a multiple Availability Zone deployment. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.optionGroup">optionGroup</a></code> | <code>aws-cdk-lib.aws_rds.IOptionGroup</code> | The option group to associate with the instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.parameterGroup">parameterGroup</a></code> | <code>aws-cdk-lib.aws_rds.IParameterGroup</code> | The DB parameter group to associate with the instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.performanceInsightEncryptionKey">performanceInsightEncryptionKey</a></code> | <code>aws-cdk-lib.aws_kms.IKey</code> | The AWS KMS key for encryption of Performance Insights data. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.performanceInsightRetention">performanceInsightRetention</a></code> | <code>aws-cdk-lib.aws_rds.PerformanceInsightRetention</code> | The amount of time, in days, to retain Performance Insights data. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.port">port</a></code> | <code>number</code> | The port for the instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.preferredBackupWindow">preferredBackupWindow</a></code> | <code>string</code> | The daily time range during which automated backups are performed. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.preferredMaintenanceWindow">preferredMaintenanceWindow</a></code> | <code>string</code> | The weekly time range (in UTC) during which system maintenance can occur. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.processorFeatures">processorFeatures</a></code> | <code>aws-cdk-lib.aws_rds.ProcessorFeatures</code> | The number of CPU cores and the number of threads per core. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.publiclyAccessible">publiclyAccessible</a></code> | <code>boolean</code> | Indicates whether the DB instance is an internet-facing instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.removalPolicy">removalPolicy</a></code> | <code>aws-cdk-lib.RemovalPolicy</code> | The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.s3ExportBuckets">s3ExportBuckets</a></code> | <code>aws-cdk-lib.aws_s3.IBucket[]</code> | S3 buckets that you want to load data into. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.s3ExportRole">s3ExportRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be associated with this DB instance to enable S3 export. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.s3ImportBuckets">s3ImportBuckets</a></code> | <code>aws-cdk-lib.aws_s3.IBucket[]</code> | S3 buckets that you want to load data from. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.s3ImportRole">s3ImportRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | Role that will be associated with this DB instance to enable S3 import. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.securityGroups">securityGroups</a></code> | <code>aws-cdk-lib.aws_ec2.ISecurityGroup[]</code> | The security groups to assign to the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.storageType">storageType</a></code> | <code>aws-cdk-lib.aws_rds.StorageType</code> | The storage type. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.subnetGroup">subnetGroup</a></code> | <code>aws-cdk-lib.aws_rds.ISubnetGroup</code> | Existing subnet group for the instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.vpcSubnets">vpcSubnets</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | The type of subnets to add to the created DB subnet group. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.engine">engine</a></code> | <code>aws-cdk-lib.aws_rds.IInstanceEngine</code> | The database engine. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.allocatedStorage">allocatedStorage</a></code> | <code>number</code> | The allocated storage size, specified in gibibytes (GiB). |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.allowMajorVersionUpgrade">allowMajorVersionUpgrade</a></code> | <code>boolean</code> | Whether to allow major version upgrades. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.databaseName">databaseName</a></code> | <code>string</code> | The name of the database. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.instanceType">instanceType</a></code> | <code>aws-cdk-lib.aws_ec2.InstanceType</code> | The name of the compute and memory capacity for the instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.licenseModel">licenseModel</a></code> | <code>aws-cdk-lib.aws_rds.LicenseModel</code> | The license model. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.parameters">parameters</a></code> | <code>{[ key: string ]: string}</code> | The parameters in the DBParameterGroup to create automatically. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.timezone">timezone</a></code> | <code>string</code> | The time zone of the instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.characterSetName">characterSetName</a></code> | <code>string</code> | For supported engines, specifies the character set to associate with the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.credentials">credentials</a></code> | <code>aws-cdk-lib.aws_rds.Credentials</code> | Credentials for the administrative user. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.storageEncrypted">storageEncrypted</a></code> | <code>boolean</code> | Indicates whether the DB instance is encrypted. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.storageEncryptionKey">storageEncryptionKey</a></code> | <code>aws-cdk-lib.aws_kms.IKey</code> | The KMS key that's used to encrypt the DB instance. |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.pgstacDbName">pgstacDbName</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.pgstacUsername">pgstacUsername</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.pgstacVersion">pgstacVersion</a></code> | <code>string</code> | *No description.* |
| <code><a href="#cdk-pgstac.PgStacDatabaseProps.property.secretsPrefix">secretsPrefix</a></code> | <code>string</code> | *No description.* |

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="cdk-pgstac.PgStacDatabaseProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

The VPC network where the DB subnet group should be created.

---

##### `autoMinorVersionUpgrade`<sup>Optional</sup> <a name="autoMinorVersionUpgrade" id="cdk-pgstac.PgStacDatabaseProps.property.autoMinorVersionUpgrade"></a>

```typescript
public readonly autoMinorVersionUpgrade: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window.

---

##### `availabilityZone`<sup>Optional</sup> <a name="availabilityZone" id="cdk-pgstac.PgStacDatabaseProps.property.availabilityZone"></a>

```typescript
public readonly availabilityZone: string;
```

- *Type:* string
- *Default:* no preference

The name of the Availability Zone where the DB instance will be located.

---

##### `backupRetention`<sup>Optional</sup> <a name="backupRetention" id="cdk-pgstac.PgStacDatabaseProps.property.backupRetention"></a>

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

##### `cloudwatchLogsExports`<sup>Optional</sup> <a name="cloudwatchLogsExports" id="cdk-pgstac.PgStacDatabaseProps.property.cloudwatchLogsExports"></a>

```typescript
public readonly cloudwatchLogsExports: string[];
```

- *Type:* string[]
- *Default:* no log exports

The list of log types that need to be enabled for exporting to CloudWatch Logs.

---

##### `cloudwatchLogsRetention`<sup>Optional</sup> <a name="cloudwatchLogsRetention" id="cdk-pgstac.PgStacDatabaseProps.property.cloudwatchLogsRetention"></a>

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

##### `cloudwatchLogsRetentionRole`<sup>Optional</sup> <a name="cloudwatchLogsRetentionRole" id="cdk-pgstac.PgStacDatabaseProps.property.cloudwatchLogsRetentionRole"></a>

```typescript
public readonly cloudwatchLogsRetentionRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* a new role is created.

The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

---

##### `copyTagsToSnapshot`<sup>Optional</sup> <a name="copyTagsToSnapshot" id="cdk-pgstac.PgStacDatabaseProps.property.copyTagsToSnapshot"></a>

```typescript
public readonly copyTagsToSnapshot: boolean;
```

- *Type:* boolean
- *Default:* true

Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance.

---

##### `deleteAutomatedBackups`<sup>Optional</sup> <a name="deleteAutomatedBackups" id="cdk-pgstac.PgStacDatabaseProps.property.deleteAutomatedBackups"></a>

```typescript
public readonly deleteAutomatedBackups: boolean;
```

- *Type:* boolean
- *Default:* false

Indicates whether automated backups should be deleted or retained when you delete a DB instance.

---

##### `deletionProtection`<sup>Optional</sup> <a name="deletionProtection" id="cdk-pgstac.PgStacDatabaseProps.property.deletionProtection"></a>

```typescript
public readonly deletionProtection: boolean;
```

- *Type:* boolean
- *Default:* true if ``removalPolicy`` is RETAIN, false otherwise

Indicates whether the DB instance should have deletion protection enabled.

---

##### `domain`<sup>Optional</sup> <a name="domain" id="cdk-pgstac.PgStacDatabaseProps.property.domain"></a>

```typescript
public readonly domain: string;
```

- *Type:* string
- *Default:* Do not join domain

The Active Directory directory ID to create the DB instance in.

---

##### `domainRole`<sup>Optional</sup> <a name="domainRole" id="cdk-pgstac.PgStacDatabaseProps.property.domainRole"></a>

```typescript
public readonly domainRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* The role will be created for you if {@link DatabaseInstanceNewProps#domain} is specified

The IAM role to be used when making API calls to the Directory Service.

The role needs the AWS-managed policy
AmazonRDSDirectoryServiceAccess or equivalent.

---

##### `enablePerformanceInsights`<sup>Optional</sup> <a name="enablePerformanceInsights" id="cdk-pgstac.PgStacDatabaseProps.property.enablePerformanceInsights"></a>

```typescript
public readonly enablePerformanceInsights: boolean;
```

- *Type:* boolean
- *Default:* false, unless ``performanceInsightRentention`` or ``performanceInsightEncryptionKey`` is set.

Whether to enable Performance Insights for the DB instance.

---

##### `iamAuthentication`<sup>Optional</sup> <a name="iamAuthentication" id="cdk-pgstac.PgStacDatabaseProps.property.iamAuthentication"></a>

```typescript
public readonly iamAuthentication: boolean;
```

- *Type:* boolean
- *Default:* false

Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

---

##### `instanceIdentifier`<sup>Optional</sup> <a name="instanceIdentifier" id="cdk-pgstac.PgStacDatabaseProps.property.instanceIdentifier"></a>

```typescript
public readonly instanceIdentifier: string;
```

- *Type:* string
- *Default:* a CloudFormation generated name

A name for the DB instance.

If you specify a name, AWS CloudFormation
converts it to lowercase.

---

##### `iops`<sup>Optional</sup> <a name="iops" id="cdk-pgstac.PgStacDatabaseProps.property.iops"></a>

```typescript
public readonly iops: number;
```

- *Type:* number
- *Default:* no provisioned iops

The number of I/O operations per second (IOPS) that the database provisions.

The value must be equal to or greater than 1000.

---

##### `maxAllocatedStorage`<sup>Optional</sup> <a name="maxAllocatedStorage" id="cdk-pgstac.PgStacDatabaseProps.property.maxAllocatedStorage"></a>

```typescript
public readonly maxAllocatedStorage: number;
```

- *Type:* number
- *Default:* No autoscaling of RDS instance

Upper limit to which RDS can scale the storage in GiB(Gibibyte).

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html#USER_PIOPS.Autoscaling](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html#USER_PIOPS.Autoscaling)

---

##### `monitoringInterval`<sup>Optional</sup> <a name="monitoringInterval" id="cdk-pgstac.PgStacDatabaseProps.property.monitoringInterval"></a>

```typescript
public readonly monitoringInterval: Duration;
```

- *Type:* aws-cdk-lib.Duration
- *Default:* no enhanced monitoring

The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance.

---

##### `monitoringRole`<sup>Optional</sup> <a name="monitoringRole" id="cdk-pgstac.PgStacDatabaseProps.property.monitoringRole"></a>

```typescript
public readonly monitoringRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole
- *Default:* A role is automatically created for you

Role that will be used to manage DB instance monitoring.

---

##### `multiAz`<sup>Optional</sup> <a name="multiAz" id="cdk-pgstac.PgStacDatabaseProps.property.multiAz"></a>

```typescript
public readonly multiAz: boolean;
```

- *Type:* boolean
- *Default:* false

Specifies if the database instance is a multiple Availability Zone deployment.

---

##### `optionGroup`<sup>Optional</sup> <a name="optionGroup" id="cdk-pgstac.PgStacDatabaseProps.property.optionGroup"></a>

```typescript
public readonly optionGroup: IOptionGroup;
```

- *Type:* aws-cdk-lib.aws_rds.IOptionGroup
- *Default:* no option group

The option group to associate with the instance.

---

##### `parameterGroup`<sup>Optional</sup> <a name="parameterGroup" id="cdk-pgstac.PgStacDatabaseProps.property.parameterGroup"></a>

```typescript
public readonly parameterGroup: IParameterGroup;
```

- *Type:* aws-cdk-lib.aws_rds.IParameterGroup
- *Default:* no parameter group

The DB parameter group to associate with the instance.

---

##### `performanceInsightEncryptionKey`<sup>Optional</sup> <a name="performanceInsightEncryptionKey" id="cdk-pgstac.PgStacDatabaseProps.property.performanceInsightEncryptionKey"></a>

```typescript
public readonly performanceInsightEncryptionKey: IKey;
```

- *Type:* aws-cdk-lib.aws_kms.IKey
- *Default:* default master key

The AWS KMS key for encryption of Performance Insights data.

---

##### `performanceInsightRetention`<sup>Optional</sup> <a name="performanceInsightRetention" id="cdk-pgstac.PgStacDatabaseProps.property.performanceInsightRetention"></a>

```typescript
public readonly performanceInsightRetention: PerformanceInsightRetention;
```

- *Type:* aws-cdk-lib.aws_rds.PerformanceInsightRetention
- *Default:* 7

The amount of time, in days, to retain Performance Insights data.

---

##### `port`<sup>Optional</sup> <a name="port" id="cdk-pgstac.PgStacDatabaseProps.property.port"></a>

```typescript
public readonly port: number;
```

- *Type:* number
- *Default:* the default port for the chosen engine.

The port for the instance.

---

##### `preferredBackupWindow`<sup>Optional</sup> <a name="preferredBackupWindow" id="cdk-pgstac.PgStacDatabaseProps.property.preferredBackupWindow"></a>

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

##### `preferredMaintenanceWindow`<sup>Optional</sup> <a name="preferredMaintenanceWindow" id="cdk-pgstac.PgStacDatabaseProps.property.preferredMaintenanceWindow"></a>

```typescript
public readonly preferredMaintenanceWindow: string;
```

- *Type:* string
- *Default:* a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#Concepts.DBMaintenance

The weekly time range (in UTC) during which system maintenance can occur.

Format: `ddd:hh24:mi-ddd:hh24:mi`
Constraint: Minimum 30-minute window

---

##### `processorFeatures`<sup>Optional</sup> <a name="processorFeatures" id="cdk-pgstac.PgStacDatabaseProps.property.processorFeatures"></a>

```typescript
public readonly processorFeatures: ProcessorFeatures;
```

- *Type:* aws-cdk-lib.aws_rds.ProcessorFeatures
- *Default:* the default number of CPU cores and threads per core for the chosen instance class.  See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor

The number of CPU cores and the number of threads per core.

---

##### `publiclyAccessible`<sup>Optional</sup> <a name="publiclyAccessible" id="cdk-pgstac.PgStacDatabaseProps.property.publiclyAccessible"></a>

```typescript
public readonly publiclyAccessible: boolean;
```

- *Type:* boolean
- *Default:* `true` if `vpcSubnets` is `subnetType: SubnetType.PUBLIC`, `false` otherwise

Indicates whether the DB instance is an internet-facing instance.

---

##### `removalPolicy`<sup>Optional</sup> <a name="removalPolicy" id="cdk-pgstac.PgStacDatabaseProps.property.removalPolicy"></a>

```typescript
public readonly removalPolicy: RemovalPolicy;
```

- *Type:* aws-cdk-lib.RemovalPolicy
- *Default:* RemovalPolicy.SNAPSHOT (remove the resource, but retain a snapshot of the data)

The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update.

---

##### `s3ExportBuckets`<sup>Optional</sup> <a name="s3ExportBuckets" id="cdk-pgstac.PgStacDatabaseProps.property.s3ExportBuckets"></a>

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

##### `s3ExportRole`<sup>Optional</sup> <a name="s3ExportRole" id="cdk-pgstac.PgStacDatabaseProps.property.s3ExportRole"></a>

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

##### `s3ImportBuckets`<sup>Optional</sup> <a name="s3ImportBuckets" id="cdk-pgstac.PgStacDatabaseProps.property.s3ImportBuckets"></a>

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

##### `s3ImportRole`<sup>Optional</sup> <a name="s3ImportRole" id="cdk-pgstac.PgStacDatabaseProps.property.s3ImportRole"></a>

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

##### `securityGroups`<sup>Optional</sup> <a name="securityGroups" id="cdk-pgstac.PgStacDatabaseProps.property.securityGroups"></a>

```typescript
public readonly securityGroups: ISecurityGroup[];
```

- *Type:* aws-cdk-lib.aws_ec2.ISecurityGroup[]
- *Default:* a new security group is created

The security groups to assign to the DB instance.

---

##### `storageType`<sup>Optional</sup> <a name="storageType" id="cdk-pgstac.PgStacDatabaseProps.property.storageType"></a>

```typescript
public readonly storageType: StorageType;
```

- *Type:* aws-cdk-lib.aws_rds.StorageType
- *Default:* GP2

The storage type.

Storage types supported are gp2, io1, standard.

> [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#Concepts.Storage.GeneralSSD](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#Concepts.Storage.GeneralSSD)

---

##### `subnetGroup`<sup>Optional</sup> <a name="subnetGroup" id="cdk-pgstac.PgStacDatabaseProps.property.subnetGroup"></a>

```typescript
public readonly subnetGroup: ISubnetGroup;
```

- *Type:* aws-cdk-lib.aws_rds.ISubnetGroup
- *Default:* a new subnet group will be created.

Existing subnet group for the instance.

---

##### `vpcSubnets`<sup>Optional</sup> <a name="vpcSubnets" id="cdk-pgstac.PgStacDatabaseProps.property.vpcSubnets"></a>

```typescript
public readonly vpcSubnets: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection
- *Default:* private subnets

The type of subnets to add to the created DB subnet group.

---

##### `engine`<sup>Required</sup> <a name="engine" id="cdk-pgstac.PgStacDatabaseProps.property.engine"></a>

```typescript
public readonly engine: IInstanceEngine;
```

- *Type:* aws-cdk-lib.aws_rds.IInstanceEngine

The database engine.

---

##### `allocatedStorage`<sup>Optional</sup> <a name="allocatedStorage" id="cdk-pgstac.PgStacDatabaseProps.property.allocatedStorage"></a>

```typescript
public readonly allocatedStorage: number;
```

- *Type:* number
- *Default:* 100

The allocated storage size, specified in gibibytes (GiB).

---

##### `allowMajorVersionUpgrade`<sup>Optional</sup> <a name="allowMajorVersionUpgrade" id="cdk-pgstac.PgStacDatabaseProps.property.allowMajorVersionUpgrade"></a>

```typescript
public readonly allowMajorVersionUpgrade: boolean;
```

- *Type:* boolean
- *Default:* false

Whether to allow major version upgrades.

---

##### `databaseName`<sup>Optional</sup> <a name="databaseName" id="cdk-pgstac.PgStacDatabaseProps.property.databaseName"></a>

```typescript
public readonly databaseName: string;
```

- *Type:* string
- *Default:* no name

The name of the database.

---

##### `instanceType`<sup>Optional</sup> <a name="instanceType" id="cdk-pgstac.PgStacDatabaseProps.property.instanceType"></a>

```typescript
public readonly instanceType: InstanceType;
```

- *Type:* aws-cdk-lib.aws_ec2.InstanceType
- *Default:* m5.large (or, more specifically, db.m5.large)

The name of the compute and memory capacity for the instance.

---

##### `licenseModel`<sup>Optional</sup> <a name="licenseModel" id="cdk-pgstac.PgStacDatabaseProps.property.licenseModel"></a>

```typescript
public readonly licenseModel: LicenseModel;
```

- *Type:* aws-cdk-lib.aws_rds.LicenseModel
- *Default:* RDS default license model

The license model.

---

##### `parameters`<sup>Optional</sup> <a name="parameters" id="cdk-pgstac.PgStacDatabaseProps.property.parameters"></a>

```typescript
public readonly parameters: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}
- *Default:* None

The parameters in the DBParameterGroup to create automatically.

You can only specify parameterGroup or parameters but not both.
You need to use a versioned engine to auto-generate a DBParameterGroup.

---

##### `timezone`<sup>Optional</sup> <a name="timezone" id="cdk-pgstac.PgStacDatabaseProps.property.timezone"></a>

```typescript
public readonly timezone: string;
```

- *Type:* string
- *Default:* RDS default timezone

The time zone of the instance.

This is currently supported only by Microsoft Sql Server.

---

##### `characterSetName`<sup>Optional</sup> <a name="characterSetName" id="cdk-pgstac.PgStacDatabaseProps.property.characterSetName"></a>

```typescript
public readonly characterSetName: string;
```

- *Type:* string
- *Default:* RDS default character set name

For supported engines, specifies the character set to associate with the DB instance.

---

##### `credentials`<sup>Optional</sup> <a name="credentials" id="cdk-pgstac.PgStacDatabaseProps.property.credentials"></a>

```typescript
public readonly credentials: Credentials;
```

- *Type:* aws-cdk-lib.aws_rds.Credentials
- *Default:* A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password

Credentials for the administrative user.

---

##### `storageEncrypted`<sup>Optional</sup> <a name="storageEncrypted" id="cdk-pgstac.PgStacDatabaseProps.property.storageEncrypted"></a>

```typescript
public readonly storageEncrypted: boolean;
```

- *Type:* boolean
- *Default:* true if storageEncryptionKey has been provided, false otherwise

Indicates whether the DB instance is encrypted.

---

##### `storageEncryptionKey`<sup>Optional</sup> <a name="storageEncryptionKey" id="cdk-pgstac.PgStacDatabaseProps.property.storageEncryptionKey"></a>

```typescript
public readonly storageEncryptionKey: IKey;
```

- *Type:* aws-cdk-lib.aws_kms.IKey
- *Default:* default master key if storageEncrypted is true, no key otherwise

The KMS key that's used to encrypt the DB instance.

---

##### `pgstacDbName`<sup>Optional</sup> <a name="pgstacDbName" id="cdk-pgstac.PgStacDatabaseProps.property.pgstacDbName"></a>

```typescript
public readonly pgstacDbName: string;
```

- *Type:* string

---

##### `pgstacUsername`<sup>Optional</sup> <a name="pgstacUsername" id="cdk-pgstac.PgStacDatabaseProps.property.pgstacUsername"></a>

```typescript
public readonly pgstacUsername: string;
```

- *Type:* string

---

##### `pgstacVersion`<sup>Optional</sup> <a name="pgstacVersion" id="cdk-pgstac.PgStacDatabaseProps.property.pgstacVersion"></a>

```typescript
public readonly pgstacVersion: string;
```

- *Type:* string

---

##### `secretsPrefix`<sup>Optional</sup> <a name="secretsPrefix" id="cdk-pgstac.PgStacDatabaseProps.property.secretsPrefix"></a>

```typescript
public readonly secretsPrefix: string;
```

- *Type:* string

---

### StacIngestorProps <a name="StacIngestorProps" id="cdk-pgstac.StacIngestorProps"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.StacIngestorProps.Initializer"></a>

```typescript
import { StacIngestorProps } from 'cdk-pgstac'

const stacIngestorProps: StacIngestorProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.dataAccessRole">dataAccessRole</a></code> | <code>aws-cdk-lib.aws_iam.IRole</code> | ARN of AWS Role used to validate access to S3 data. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.stacDbSecret">stacDbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing pgSTAC DB connection information. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.stacDbSecurityGroup">stacDbSecurityGroup</a></code> | <code>aws-cdk-lib.aws_ec2.ISecurityGroup</code> | Security Group used by pgSTAC DB. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.stacUrl">stacUrl</a></code> | <code>string</code> | URL of STAC API. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.stage">stage</a></code> | <code>string</code> | Stage of deployment (e.g. `dev`, `prod`). |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Boolean indicating whether or not pgSTAC DB is in a public subnet. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC running pgSTAC DB. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.apiEndpointConfiguration">apiEndpointConfiguration</a></code> | <code>aws-cdk-lib.aws_apigateway.EndpointConfiguration</code> | API Endpoint Configuration, useful for creating private APIs. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Environment variables to be sent to Lambda. |
| <code><a href="#cdk-pgstac.StacIngestorProps.property.apiPolicy">apiPolicy</a></code> | <code>aws-cdk-lib.aws_iam.PolicyDocument</code> | API Policy Document, useful for creating private APIs. |

---

##### `dataAccessRole`<sup>Required</sup> <a name="dataAccessRole" id="cdk-pgstac.StacIngestorProps.property.dataAccessRole"></a>

```typescript
public readonly dataAccessRole: IRole;
```

- *Type:* aws-cdk-lib.aws_iam.IRole

ARN of AWS Role used to validate access to S3 data.

---

##### `stacDbSecret`<sup>Required</sup> <a name="stacDbSecret" id="cdk-pgstac.StacIngestorProps.property.stacDbSecret"></a>

```typescript
public readonly stacDbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing pgSTAC DB connection information.

---

##### `stacDbSecurityGroup`<sup>Required</sup> <a name="stacDbSecurityGroup" id="cdk-pgstac.StacIngestorProps.property.stacDbSecurityGroup"></a>

```typescript
public readonly stacDbSecurityGroup: ISecurityGroup;
```

- *Type:* aws-cdk-lib.aws_ec2.ISecurityGroup

Security Group used by pgSTAC DB.

---

##### `stacUrl`<sup>Required</sup> <a name="stacUrl" id="cdk-pgstac.StacIngestorProps.property.stacUrl"></a>

```typescript
public readonly stacUrl: string;
```

- *Type:* string

URL of STAC API.

---

##### `stage`<sup>Required</sup> <a name="stage" id="cdk-pgstac.StacIngestorProps.property.stage"></a>

```typescript
public readonly stage: string;
```

- *Type:* string

Stage of deployment (e.g. `dev`, `prod`).

---

##### `subnetSelection`<sup>Required</sup> <a name="subnetSelection" id="cdk-pgstac.StacIngestorProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Boolean indicating whether or not pgSTAC DB is in a public subnet.

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="cdk-pgstac.StacIngestorProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC running pgSTAC DB.

---

##### `apiEndpointConfiguration`<sup>Optional</sup> <a name="apiEndpointConfiguration" id="cdk-pgstac.StacIngestorProps.property.apiEndpointConfiguration"></a>

```typescript
public readonly apiEndpointConfiguration: EndpointConfiguration;
```

- *Type:* aws-cdk-lib.aws_apigateway.EndpointConfiguration

API Endpoint Configuration, useful for creating private APIs.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="cdk-pgstac.StacIngestorProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Environment variables to be sent to Lambda.

---

##### `apiPolicy`<sup>Optional</sup> <a name="apiPolicy" id="cdk-pgstac.StacIngestorProps.property.apiPolicy"></a>

```typescript
public readonly apiPolicy: PolicyDocument;
```

- *Type:* aws-cdk-lib.aws_iam.PolicyDocument

API Policy Document, useful for creating private APIs.

---

### TitilerPgStacApiLambdaProps <a name="TitilerPgStacApiLambdaProps" id="cdk-pgstac.TitilerPgStacApiLambdaProps"></a>

#### Initializer <a name="Initializer" id="cdk-pgstac.TitilerPgStacApiLambdaProps.Initializer"></a>

```typescript
import { TitilerPgStacApiLambdaProps } from 'cdk-pgstac'

const titilerPgStacApiLambdaProps: TitilerPgStacApiLambdaProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps.property.db">db</a></code> | <code>aws-cdk-lib.aws_rds.IDatabaseInstance</code> | RDS Instance with installed pgSTAC. |
| <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps.property.dbSecret">dbSecret</a></code> | <code>aws-cdk-lib.aws_secretsmanager.ISecret</code> | Secret containing connection information for pgSTAC database. |
| <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps.property.subnetSelection">subnetSelection</a></code> | <code>aws-cdk-lib.aws_ec2.SubnetSelection</code> | Subnet into which the lambda should be deployed. |
| <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps.property.vpc">vpc</a></code> | <code>aws-cdk-lib.aws_ec2.IVpc</code> | VPC into which the lambda should be deployed. |
| <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps.property.apiEnv">apiEnv</a></code> | <code>{[ key: string ]: string}</code> | Customized environment variables to send to titiler-pgstac runtime. |
| <code><a href="#cdk-pgstac.TitilerPgStacApiLambdaProps.property.buckets">buckets</a></code> | <code>string[]</code> | list of buckets the lambda will be granted access to. |

---

##### `db`<sup>Required</sup> <a name="db" id="cdk-pgstac.TitilerPgStacApiLambdaProps.property.db"></a>

```typescript
public readonly db: IDatabaseInstance;
```

- *Type:* aws-cdk-lib.aws_rds.IDatabaseInstance

RDS Instance with installed pgSTAC.

---

##### `dbSecret`<sup>Required</sup> <a name="dbSecret" id="cdk-pgstac.TitilerPgStacApiLambdaProps.property.dbSecret"></a>

```typescript
public readonly dbSecret: ISecret;
```

- *Type:* aws-cdk-lib.aws_secretsmanager.ISecret

Secret containing connection information for pgSTAC database.

---

##### `subnetSelection`<sup>Required</sup> <a name="subnetSelection" id="cdk-pgstac.TitilerPgStacApiLambdaProps.property.subnetSelection"></a>

```typescript
public readonly subnetSelection: SubnetSelection;
```

- *Type:* aws-cdk-lib.aws_ec2.SubnetSelection

Subnet into which the lambda should be deployed.

---

##### `vpc`<sup>Required</sup> <a name="vpc" id="cdk-pgstac.TitilerPgStacApiLambdaProps.property.vpc"></a>

```typescript
public readonly vpc: IVpc;
```

- *Type:* aws-cdk-lib.aws_ec2.IVpc

VPC into which the lambda should be deployed.

---

##### `apiEnv`<sup>Optional</sup> <a name="apiEnv" id="cdk-pgstac.TitilerPgStacApiLambdaProps.property.apiEnv"></a>

```typescript
public readonly apiEnv: {[ key: string ]: string};
```

- *Type:* {[ key: string ]: string}

Customized environment variables to send to titiler-pgstac runtime.

---

##### `buckets`<sup>Optional</sup> <a name="buckets" id="cdk-pgstac.TitilerPgStacApiLambdaProps.property.buckets"></a>

```typescript
public readonly buckets: string[];
```

- *Type:* string[]

list of buckets the lambda will be granted access to.

---



