import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface PatchManagerProps {
  /** 
   * The EC2 instance ID to apply patches
   */
  instanceId: string;

  /**
   * Custom maintenance window
   *
   * @default - New maintenance window
   * schedule: Sundays at 07:00 UTC, duration: 3 hours, cutoff: 1 hour
   */
  maintenanceWindow?: ssm.CfnMaintenanceWindow;
}

export class PatchManager extends Construct {
  constructor(scope: Construct, id: string, props?: PatchManagerProps) {
    super(scope, id);

    // IAM role used by the maintenance window
    const maintenanceRole = new iam.Role(this, 'MaintenanceWindowRole', {
      assumedBy: new iam.ServicePrincipal('ssm.amazonaws.com'),
    });

    maintenanceRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          'ssm:SendCommand',
          'ssm:ListCommands',
          'ssm:ListCommandInvocations',
        ],
        resources: ['*'],
      }),
    );

    // Maintenance Window
    const maintenanceWindow = props?.maintenanceWindow ?? new ssm.CfnMaintenanceWindow(
      this,
      'PatchMaintenanceWindow',
      {
        name: 'patch-maintenance-window',
        description: 'Weekly patching using AWS default patch baseline',
        schedule: 'cron(0 7 ? * SUN *)', // Sundays 07:00 UTC
        duration: 3,
        cutoff: 1,
        allowUnassociatedTargets: false,
      },
    );

    // Target EC2 instance by Instance ID
    if (!props?.instanceId) {
      throw new Error('instanceId is required to create PatchManagerStack');
    }
    const target = new ssm.CfnMaintenanceWindowTarget(
      this,
      'PatchTarget',
      {
        windowId: maintenanceWindow.ref,
        resourceType: 'INSTANCE',
        targets: [
          {
            key: 'InstanceIds',
            values: [props.instanceId],
          },
        ],
      },
    );

    // Patch task (Install)
    new ssm.CfnMaintenanceWindowTask(this, 'PatchInstallTask', {
      windowId: maintenanceWindow.ref,
      taskArn: 'AWS-RunPatchBaseline',
      taskType: 'RUN_COMMAND',
      priority: 1,
      maxConcurrency: '1',
      maxErrors: '1',
      serviceRoleArn: maintenanceRole.roleArn,
      targets: [
        {
          key: 'WindowTargetIds',
          values: [target.ref],
        },
      ],
      taskInvocationParameters: {
        maintenanceWindowRunCommandParameters: {
          parameters: {
            Operation: ['Install'],
          },
        },
      },
    });
  }
}
