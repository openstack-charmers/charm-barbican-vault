# Overview

The Barbican-Vault charm provies a Vault backend for OpenStack Barbican

OpenStack Rocky or later is required.

This charm, when used with the Barbican Charm, provides a software-based
secrets-as-a-service solution for an OpenStack Cloud.  In the future, other
back-ends may be added.

# Usage

    juju deploy barbican --config openstack-origin=bionic:rocky
    juju deploy barbican-vault
    juju deploy vault
    juju add-relation barbican-vault:secrets barbican:secrets
    juju add-relation vault:secrets barbican-vault:secrets-storage

# Bugs

Please report bugs on [Launchpad](https://bugs.launchpad.net/charm-barbican-vault/+filebug).

For general questions please refer to the OpenStack [Charm Guide](https://docs.openstack.org/charm-guide/latest/).
