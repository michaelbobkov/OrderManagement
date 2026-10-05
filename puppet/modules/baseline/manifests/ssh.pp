# sshd hardening: no root login, no password auth.
class baseline::ssh {
  package { 'openssh-server':
    ensure => installed,
  }

  file { '/etc/ssh/sshd_config':
    ensure       => file,
    owner        => 'root',
    group        => 'root',
    mode         => '0600',
    source       => 'puppet:///modules/baseline/sshd_config',
    validate_cmd => '/usr/sbin/sshd -t -f %',
    require      => Package['openssh-server'],
    notify       => Service['ssh'],
  }

  service { 'ssh':
    ensure => running,
    enable => true,
  }
}
