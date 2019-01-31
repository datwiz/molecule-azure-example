# import os
import pytest


# expected installed packages
@pytest.mark.parametrize('package', [
  ('nginx'),
])
def test_installed_packages(host, package):
    pkg = host.package(package)
    assert pkg.is_installed


# expected services are running and enabled
@pytest.mark.parametrize('service', [
    ('nginx'),
])
def test_running_services(host, service):
    svc = host.service(service)
    assert svc.is_running
    assert svc.is_enabled


# expected ports listening
# note testing port binding, not firewall/network security group rules
@pytest.mark.parametrize('socket', [
    ('tcp://0.0.0.0:80'),
])
def test_port_bindings(host, socket):
    assert host.socket(socket).is_listening
