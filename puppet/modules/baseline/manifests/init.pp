# Baseline configuration applied to every VM. Re-applied every 30 minutes so
# manual drift (sshd settings, stopped services, missing packages) is reverted.
class baseline (
  Array[String] $packages       = ['curl', 'vim', 'htop', 'unzip', 'ca-certificates'],
  Array[String] $admin_users    = ['opsadmin'],
  String        $apply_interval = '*/30',
) {
  contain baseline::packages
  contain baseline::users
  contain baseline::ssh
  contain baseline::ntp
  contain baseline::node_exporter
  contain baseline::agent_cron

  Class['baseline::packages']
  -> Class['baseline::users']
  -> Class['baseline::ssh']
  -> Class['baseline::ntp']
  -> Class['baseline::node_exporter']
  -> Class['baseline::agent_cron']
}
