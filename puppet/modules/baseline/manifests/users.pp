# Admin users with passwordless sudo (SSH keys come from GCP OS Login / metadata).
class baseline::users {
  $baseline::admin_users.each |String $name| {
    user { $name:
      ensure     => present,
      managehome => true,
      shell      => '/bin/bash',
      groups     => ['sudo'],
    }
  }

  file { '/etc/sudoers.d/90-baseline-admins':
    ensure       => file,
    owner        => 'root',
    group        => 'root',
    mode         => '0440',
    content      => join($baseline::admin_users.map |$u| { "${u} ALL=(ALL) NOPASSWD:ALL" }, "\n"),
    validate_cmd => '/usr/sbin/visudo -cf %',
  }
}
