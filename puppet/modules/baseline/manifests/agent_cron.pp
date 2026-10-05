# Re-apply this manifest on a schedule so configuration drift self-heals.
class baseline::agent_cron {
  file { '/usr/local/bin/puppet-apply-baseline':
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    content => epp('baseline/puppet-apply.sh.epp'),
  }

  cron { 'puppet-apply-baseline':
    ensure  => present,
    command => '/usr/local/bin/puppet-apply-baseline >> /var/log/puppet-apply.log 2>&1',
    user    => 'root',
    minute  => $baseline::apply_interval,
    require => File['/usr/local/bin/puppet-apply-baseline'],
  }
}
