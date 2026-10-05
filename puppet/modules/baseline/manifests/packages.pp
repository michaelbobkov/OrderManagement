# Common packages.
class baseline::packages {
  package { $baseline::packages:
    ensure => installed,
  }
}
