#!/bin/bash
set -euxo pipefail

# These variables will be replaced by the TypeScript code
SECRET_ARN=${SECRET_ARN}
REGION=${REGION}
POOL_MODE=${POOL_MODE}
MAX_CLIENT_CONN=${MAX_CLIENT_CONN}
DEFAULT_POOL_SIZE=${DEFAULT_POOL_SIZE}
MIN_POOL_SIZE=${MIN_POOL_SIZE}
RESERVE_POOL_SIZE=${RESERVE_POOL_SIZE}
RESERVE_POOL_TIMEOUT=${RESERVE_POOL_TIMEOUT}
MAX_DB_CONNECTIONS=${MAX_DB_CONNECTIONS}
MAX_USER_CONNECTIONS=${MAX_USER_CONNECTIONS}
CLOUDWATCH_CONFIG="/opt/aws/amazon-cloudwatch-agent/bin/config.json"

wait_for_dpkg_lock() {
    local max_wait=300
    local elapsed=0

    while [ $elapsed -lt $max_wait ]; do
        if ! fuser /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock 2>/dev/null; then
            echo "dpkg locks are free, proceeding..."
            return 0
        fi

        echo "Waiting for dpkg locks... (${elapsed}s elapsed)"
        fuser -v /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock 2>/dev/null || true

        sleep 5
        elapsed=$((elapsed + 5))
    done

    echo "ERROR: Timeout waiting for dpkg locks after ${max_wait} seconds"
    return 1
}

if systemctl is-active --quiet unattended-upgrades 2>/dev/null; then
    echo "Stopping unattended-upgrades service temporarily..."
    systemctl stop unattended-upgrades
fi

export DEBIAN_FRONTEND=noninteractive

curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

wait_for_dpkg_lock
apt-get update

wait_for_dpkg_lock
apt-get upgrade -y

wait_for_dpkg_lock
apt-get install -y pgbouncer jq

snap install aws-cli --classic

echo "Fetching secret from ARN: ${SECRET_ARN}"

# Before handling secrets, turn off command tracing
set +x
SECRET=$(aws secretsmanager get-secret-value --secret-id ${SECRET_ARN} --region ${REGION} --query SecretString --output text)

# Parse database credentials without echoing
DB_HOST=$(echo "$SECRET" | jq -r '.host')
DB_PORT=$(echo "$SECRET" | jq -r '.port')
DB_NAME=$(echo "$SECRET" | jq -r '.dbname')
DB_USER=$(echo "$SECRET" | jq -r '.username')
DB_PASSWORD=$(echo "$SECRET" | jq -r '.password')

echo 'Creating PgBouncer configuration...'

# Create pgbouncer.ini
cat <<EOC > /etc/pgbouncer/pgbouncer.ini
[databases]
* = host=$DB_HOST port=$DB_PORT dbname=$DB_NAME

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = ${DB_PORT}
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = ${POOL_MODE}
max_client_conn = ${MAX_CLIENT_CONN}
default_pool_size = ${DEFAULT_POOL_SIZE}
min_pool_size = ${MIN_POOL_SIZE}
reserve_pool_size = ${RESERVE_POOL_SIZE}
reserve_pool_timeout = ${RESERVE_POOL_TIMEOUT}
max_db_connections = ${MAX_DB_CONNECTIONS}
max_user_connections = ${MAX_USER_CONNECTIONS}
max_prepared_statements = 10
ignore_startup_parameters = application_name,search_path
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
admin_users = $DB_USER
stats_users = $DB_USER
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
log_stats = 1
stats_period = 60
EOC

# Create userlist.txt without echoing sensitive info
{
    echo "\"$DB_USER\" \"$DB_PASSWORD\""
} > /etc/pgbouncer/userlist.txt

# Turn command tracing back on
set -x

# Set correct permissions
chown postgres:postgres /etc/pgbouncer/pgbouncer.ini /etc/pgbouncer/userlist.txt
chmod 600 /etc/pgbouncer/pgbouncer.ini /etc/pgbouncer/userlist.txt

# Configure logging
# ensure /var/run/pgbouncer gets created on boot
cat <<EOC > /etc/tmpfiles.d/pgbouncer.conf
d /var/run/pgbouncer 0755 postgres postgres -
EOC

mkdir -p /var/log/pgbouncer /var/run/pgbouncer
chown postgres:postgres /var/log/pgbouncer /var/run/pgbouncer
chmod 755 /var/log/pgbouncer /var/run/pgbouncer

touch /var/log/pgbouncer/pgbouncer.log
chown postgres:postgres /var/log/pgbouncer/pgbouncer.log
chmod 640 /var/log/pgbouncer/pgbouncer.log

# Enable and start pgbouncer service
systemctl enable pgbouncer
systemctl restart pgbouncer

cat <<EOC > /etc/logrotate.d/pgbouncer
/var/log/pgbouncer/pgbouncer.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    copytruncate
    create 640 postgres postgres
}
EOC

# Create monitoring scripts directory
mkdir -p /opt/pgbouncer/scripts

# Create the health check script
cat <<'EOC' > /opt/pgbouncer/scripts/check.sh
#!/bin/bash
echo $(/bin/systemctl is-active pgbouncer)
if ! /bin/systemctl is-active --quiet pgbouncer; then
  # If it's not active, attempt to start it
  echo "$(date): PgBouncer is not running, attempting to restart" | logger -t pgbouncer-monitor
  /bin/systemctl start pgbouncer

  # Check if the restart was successful
  if /bin/systemctl is-active --quiet pgbouncer; then
    echo "$(date): PgBouncer successfully restarted" | logger -t pgbouncer-monitor
  else
    echo "$(date): Failed to restart PgBouncer" | logger -t pgbouncer-monitor
  fi
else
  # If it's already active, no action is needed
  echo "$(date): PgBouncer is running; no action needed" | logger -t pgbouncer-monitor
fi
EOC
chmod +x /opt/pgbouncer/scripts/check.sh

# enable cron job
cat <<'EOC' > /opt/pgbouncer/scripts/crontab.txt
# PgBouncer health check - run every minute
* * * * * /opt/pgbouncer/scripts/check.sh
EOC

crontab /opt/pgbouncer/scripts/crontab.txt

if ! crontab -l; then
  echo 'Failed to install crontab' | logger -t pgbouncer-setup
  exit 1
fi

# Create CloudWatch configuration directory
mkdir -p /opt/pgbouncer/cloudwatch

# Install CloudWatch agent
if ! wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb; then
  echo 'Failed to download CloudWatch agent' | logger -t pgbouncer-setup
  exit 1
fi

wait_for_dpkg_lock
if ! dpkg -i amazon-cloudwatch-agent.deb; then
  echo 'Failed to install CloudWatch agent' | logger -t pgbouncer-setup
  exit 1
fi

# Create CloudWatch config
cat <<EOC > ${CLOUDWATCH_CONFIG}
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/pgbouncer/pgbouncer.log",
            "log_group_name": "/pgbouncer/logs",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S",
            "multi_line_start_pattern": "{timestamp_format}",
            "retention_in_days": 14
          },
          {
            "file_path": "/var/log/syslog",
            "log_group_name": "/pgbouncer/system-logs",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%b %d %H:%M:%S",
            "retention_in_days": 14
          }
        ]
      }
    }
  },
  "metrics": {
    "metrics_collected": {
      "procstat": [
        {
          "pattern": "pgbouncer",
          "measurement": [
            "cpu_usage",
            "memory_rss",
            "read_bytes",
            "write_bytes",
            "read_count",
            "write_count",
            "num_fds"
          ]
        }
      ],
      "mem": {
        "measurement": [
          "mem_used_percent"
        ]
      },
      "disk": {
        "measurement": [
          "used_percent"
        ]
      }
    },
    "aggregation_dimensions": [["InstanceId"]]
  }
}
EOC

# Verify the config file exists
if [ ! -f ${CLOUDWATCH_CONFIG} ]; then
  echo 'CloudWatch config file not created' | logger -t pgbouncer-setup
  exit 1
fi

# Start CloudWatch agent
if ! /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:${CLOUDWATCH_CONFIG}; then
  echo 'Failed to configure CloudWatch agent' | logger -t pgbouncer-setup
  exit 1
fi

systemctl enable amazon-cloudwatch-agent
systemctl start amazon-cloudwatch-agent

# Verify CloudWatch agent is running
if ! systemctl is-active amazon-cloudwatch-agent; then
  echo 'CloudWatch agent failed to start' | logger -t pgbouncer-setup
  exit 1
fi

# Configure unattended-upgrades for security updates on this long-lived instance
echo "Configuring unattended-upgrades for security updates..."

# Create optimized unattended-upgrades configuration
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
// Automatically upgrade packages from these origins
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
    // Add PostgreSQL security updates
    "apt.postgresql.org:${distro_codename}-pgdg main";
};

// Do not automatically upgrade these packages - keep manual control
Unattended-Upgrade::Package-Blacklist {
    "pgbouncer";
    "postgresql*";
    "libpq*";
};

// Automatically reboot if required after security updates
// Only during maintenance window
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";

// Send email on errors (configure your email if needed)
//Unattended-Upgrade::Mail "your-email@domain.com";
Unattended-Upgrade::MailReport "on-change";

// Remove unused automatically installed kernel-related packages
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";

// Remove unused dependencies
Unattended-Upgrade::Remove-Unused-Dependencies "true";

// Automatically remove new unused dependencies after the upgrade
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";

// Split the upgrade into the smallest possible chunks
Unattended-Upgrade::MinimalSteps "true";

// Install updates in the background
Unattended-Upgrade::InstallOnShutdown "false";
EOF

# Configure automatic update schedule
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
// Enable automatic updates
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";

// Download upgradeable packages
APT::Periodic::Download-Upgradeable-Packages "1";

// Clean local download archive
APT::Periodic::AutocleanInterval "7";

// Verbose logging for debugging
APT::Periodic::Verbose "2";
EOF

# Configure systemd timer for predictable timing
mkdir -p /etc/systemd/system/apt-daily.timer.d/
mkdir -p /etc/systemd/system/apt-daily-upgrade.timer.d/

cat > /etc/systemd/system/apt-daily.timer.d/override.conf << 'EOF'
[Timer]
# Run at 1 AM daily instead of random times
OnCalendar=
OnCalendar=01:00
RandomizedDelaySec=0
EOF

cat > /etc/systemd/system/apt-daily-upgrade.timer.d/override.conf << 'EOF'
[Timer]
# Run upgrades at 1:30 AM, after the update check
OnCalendar=
OnCalendar=01:30
RandomizedDelaySec=0
EOF

# Reload systemd and re-enable unattended-upgrades
systemctl daemon-reload
systemctl enable unattended-upgrades
systemctl start unattended-upgrades

# Enable and configure the timers
systemctl enable apt-daily.timer
systemctl enable apt-daily-upgrade.timer

echo "Setup complete!"
echo "- PgBouncer: configured and running"
echo "- CloudWatch: monitoring enabled"
echo "- Security updates: enabled (daily at 1:00-1:30 AM)"
echo "- Auto-reboot: enabled at 2:00 AM if required"
echo "- PgBouncer packages: protected from auto-updates"
echo "- Health monitoring: running every minute via cron"
