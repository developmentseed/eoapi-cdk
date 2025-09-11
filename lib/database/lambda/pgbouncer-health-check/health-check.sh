#!/bin/bash
set -euo pipefail

echo '=== PGBOUNCER HEALTH CHECK START ==='
echo 'Health check started at:' $(date)
echo ''

# Wait for cloud-init to complete before checking pgbouncer
echo '=== WAITING: Cloud-init completion check ==='
MAX_WAIT=300  # 5 minutes max wait
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
  if command -v cloud-init >/dev/null 2>&1; then
    CLOUD_INIT_STATUS=$(cloud-init status --format=json 2>/dev/null | grep '"status":' | sed 's/.*"status": *"\([^"]*\)".*/\1/' 2>/dev/null)
    echo "Cloud-init status: $CLOUD_INIT_STATUS (waited ${WAIT_COUNT}s)"
    if [ "$CLOUD_INIT_STATUS" = "done" ]; then
      echo 'SUCCESS: Cloud-init has completed'
      break
    elif [ "$CLOUD_INIT_STATUS" = "error" ]; then
      echo 'CLOUD-INIT SETUP FAILED:'
      cloud-init status --long 2>&1 || true
      echo ''
      echo 'Setup script errors:'
      tail -n 20 /var/log/cloud-init-output.log 2>&1 || echo 'Could not read setup logs'
      exit 1
    fi
  else
    echo 'Cloud-init command not available, assuming setup is complete'
    break
  fi

  if [ $WAIT_COUNT -eq 0 ]; then
    echo 'Cloud-init is still running, waiting for completion...'
  fi

  sleep 10
  WAIT_COUNT=$((WAIT_COUNT + 10))
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
  echo 'WARNING: Timed out waiting for cloud-init to complete after 10 minutes'
  echo 'Current cloud-init status:'
  cloud-init status --long || true
  echo 'Proceeding with health check anyway...'
fi

echo 'Cloud-init wait complete, now checking pgbouncer...'
echo ''

# Critical check: Verify pgbouncer service is active
echo '=== CRITICAL: PgBouncer service status ==='
if systemctl is-active --quiet pgbouncer; then
  echo 'SUCCESS: PgBouncer service is active'
  systemctl status pgbouncer --no-pager --lines=5
else
  echo 'FAILURE: PgBouncer service is NOT active'
  echo 'Service status:'
  systemctl status pgbouncer --no-pager --lines=10 || echo 'Could not get service status'
  echo 'Service is-active result:' $(systemctl is-active pgbouncer)
  echo 'Service is-enabled result:' $(systemctl is-enabled pgbouncer)
  echo 'Last 20 lines of pgbouncer systemd logs:'
  journalctl -u pgbouncer --no-pager -n 20 || echo 'Could not get pgbouncer logs'
  echo ''
  echo '=== SETUP DIAGNOSTICS: Cloud-init output log ==='
  if [ -f /var/log/cloud-init-output.log ]; then
    echo 'Last 50 lines of cloud-init-output.log to help diagnose setup issues:'
    tail -n 50 /var/log/cloud-init-output.log
  else
    echo 'Cloud-init-output.log not found'
  fi
  echo ''
  echo '=== SETUP DIAGNOSTICS: Cloud-init status ==='
  if command -v cloud-init >/dev/null 2>&1; then
    cloud-init status --long || echo 'Could not get cloud-init status'
  else
    echo 'cloud-init command not available'
  fi
  exit 1
fi

# Critical check: Verify pgbouncer is listening on port 5432
echo '=== CRITICAL: Network listening check ==='
if ss -tlnp | grep -q ':5432.*pgbouncer' || netstat -tlnp 2>/dev/null | grep -q ':5432.*pgbouncer'; then
  echo 'SUCCESS: PgBouncer is listening on port 5432'
  ss -tlnp | grep :5432 | head -3 2>/dev/null || netstat -tlnp 2>/dev/null | grep :5432 | head -3
else
  echo 'FAILURE: PgBouncer is NOT listening on port 5432'
  echo 'All processes listening on 5432:'
  ss -tlnp | grep :5432 2>/dev/null || netstat -tlnp 2>/dev/null | grep :5432 || echo 'No processes listening on port 5432'
  echo 'All pgbouncer processes:'
  ps aux | grep pgbouncer | grep -v grep || echo 'No pgbouncer processes running'
  exit 1
fi

# Critical check: Test TCP connection to pgbouncer
echo '=== CRITICAL: Connection test ==='
if timeout 10 bash -c "</dev/tcp/localhost/5432"; then
  echo 'SUCCESS: TCP connection to localhost:5432 successful'
else
  echo 'FAILURE: TCP connection to localhost:5432 failed'
  echo 'Connection test failed - pgbouncer may not be responding'
  exit 1
fi

# Detailed diagnostics (only if basic checks pass)
echo '=== DIAGNOSTICS: Additional information ==='
echo 'System uptime:' $(uptime)

# Check pgbouncer configuration
if [ -f /etc/pgbouncer/pgbouncer.ini ]; then
  echo 'PgBouncer config exists:'
  ls -la /etc/pgbouncer/pgbouncer.ini
  echo 'Key config settings:'
  grep -E '^(listen_|pool_mode|max_|default_pool_size)' /etc/pgbouncer/pgbouncer.ini | head -10
else
  echo 'WARNING: PgBouncer config not found'
fi

# Check pgbouncer logs for recent activity
if [ -f /var/log/pgbouncer/pgbouncer.log ]; then
  echo 'Recent pgbouncer log entries (last 10 lines):'
  tail -n 10 /var/log/pgbouncer/pgbouncer.log
else
  echo 'PgBouncer log not found'
fi

# Check if setup is still running (should be done by now)
if pgrep -af cloud-init > /dev/null || pgrep -af 'pgbouncer.*setup' > /dev/null; then
  echo 'WARNING: Setup processes still running - this may indicate setup incomplete'
  ps aux | grep -E '(cloud-init|setup)' | grep -v grep || true
fi

echo '=== SUCCESS: All critical checks passed ==='
echo 'PgBouncer is running and accessible on port 5432'
echo 'Health check completed at:' $(date)
