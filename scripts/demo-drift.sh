#!/usr/bin/env bash
# Demonstrate Puppet drift correction on an app VM.
# Usage: demo-drift.sh <vm-name> [zone]
set -euo pipefail
VM="${1:?vm name}"; ZONE="${2:-us-central1-a}"
ssh_vm() { gcloud compute ssh "$VM" --zone "$ZONE" --command "$1"; }

echo "== Introduce drift: weaken sshd and stop chrony =="
ssh_vm "sudo sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config; sudo systemctl stop chrony || sudo systemctl stop chronyd"
echo "== Drifted state =="
ssh_vm "grep PermitRootLogin /etc/ssh/sshd_config; systemctl is-active chrony || systemctl is-active chronyd || true"
echo "== Run puppet agent (normally runs every 30 min via cron) =="
ssh_vm "sudo /opt/puppetlabs/bin/puppet agent --test || true"
echo "== Corrected state =="
ssh_vm "grep PermitRootLogin /etc/ssh/sshd_config; systemctl is-active chrony || systemctl is-active chronyd"
