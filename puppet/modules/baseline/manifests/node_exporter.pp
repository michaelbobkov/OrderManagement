# Prometheus node_exporter (Debian package) so host CPU/memory is scraped.
class baseline::node_exporter {
  package { 'prometheus-node-exporter':
    ensure => installed,
  }

  service { 'prometheus-node-exporter':
    ensure  => running,
    enable  => true,
    require => Package['prometheus-node-exporter'],
  }
}
