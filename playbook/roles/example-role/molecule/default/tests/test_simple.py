# simple testinfra infrastructure tests


def test_installed_packages(host):
    assert host.package('nginx').is_installed


def test_running_services(host):
    svc = host.service('nginx')
    assert svc.is_running
    assert svc.is_enabled


# expected ports listening
# note testing port binding, not firewall/network security group rules
def test_port_bindings(host):
    assert host.socket('tcp://0.0.0.0:80').is_listening
