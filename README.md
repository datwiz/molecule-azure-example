# Infracode using molecule on Azure
A few years back, before the rise of the hyper-scalers, I had my first infracode 'aha moment' with an OpenStack.  

The second came with test-kitchen.

I had already been using test driven development for application code and configuration automation for infrastructure
but test-kitchen brought the two together.  test-kitchen made it possible to write tests, spin up infrastructure, and then
tear everything down again.  The Red/Green/Refactor cycle for infrastructure.  What made this even better was that it wasn't
a facsimile of a target environment, it was the same - same VM's, same OS, same network.

Coming from Chef configuration automation, test-kitchen is a great fit to the ruby ecosystem.

test-kitchen works with ansible and azure, but a ruby environment and at least a smattering of ruby coding skills.
molecule provides a similar red-green development cycle to test-kitchen, but without the need to step outside
of the familiar python environment.

## Molecule: An all Python stack
Ansible with [molecule](https://molecule.readthedocs.io/) delivers an all python dev/test stack
for test driven infrastructure and testing automation.  

### molecule with roles
molecule can be configured to test collections of roles in playbooks

### molecule with playbooks
molecule can be configured to test an individual role.  This is a tutorial on using molecule to develop and
test an individual ansible role.

### Molecule infrastructure drivers
Out of the box, molecule supports development of ansible roles using either a docker or virtualbox
infrastructure provider.  molecule also provides drivers for private and public cloud platforms, but
with fewer examples and tutorials for cloud providers, getting up and running with molecule can be a
bit more challanging.

Local drivers like virtual box enable fast iteration of the configuration but aren't able to help with:
* running services under systemd - a typical docker container would not include a systemd supervisor
* not the same operating context - available resources and networks
* not the same OS as the target environment

### molecule on Azure
The default templates for the azure driver are geared towards a personal tutorial environment, where
you own a subscription and have the rights to create resource groups and networks with public IP
address connectivity.
In an enterprise environment, access rights is often more restrictive.
This tutorial is greared towards using ansible and molecule in an enterprise context, where an
infracode developer has access to create VM's in designated environments, but restricted in the creation
of resource groups or networks.

### A note on use of Public IP addresses
While this How-To targets an Enterprise style environment, the development VM instances do make use of Public IP addresses exposing port 22 (ssh) to the Internet.

Risk is minimised each new dev environment container instance generating a new public/private key pair for accessing the VM instances using ssh.  When the container
instance is removed, the ssh private key is destroyed.  Further, only port 22 on the VM instance is configured to accept traffic from the Internet.

Molecule uses the Ansible Azure modules for creating VM instances.  If your Azure environment provides access to VM's using a private network, the use of Public IP
addresses can be disabled by editing the `./molecule/default/create.yml` file.  

## Molecule on Azure How-To
### Infracode red/green workflow
* Red - write a failing infrastructure test
* Green - write the ansible tasks needed to pass the test
* Refactor - repeat the process

### Setup a working environment
There are a number of options for setting up a python environment for ansible and molecule, including Python virtualenv or a docker container environment.

### Azure setup
Ensure there is an existing Azure Resource Group that will be used for infracode development and testing.
Within the resource group, ensure there is a single virtual network (vnet) with a single subnet.  Ansible will use these for the default network setup.


#### 0. Creating a docker image for Ansible+Molecule+Azure
This How-To uses makes use of a docker container environment.  A dockerfile for the image can be found in `./molecule-azure-image/Dockerfile`
The image sets up a sane Python3 environment with `ansible`, `ansiblep[azure]`, and `molecule` pip modules installed.
```
$ export IMAGE_BUILD_DIRECTORY=./molecule-azure-image
$ export IMAGE_NAME=molecule-azure:latest
$ docker build -t ${IMAGE_NAME} ${IMAGE_BUILD_DIRECTORY}
```

### 1. Start a docker workspace
Setup working environment using a docker image with ansible, molecule, and the azure-cli installed
```
$ export ANSIBLE_PLAYBOOK_DIRECTORY=$(pwd)/playbook
$ docker run -it --rm --name molecule-azure -v ${ANSIBLE_PLAYBOOK_DIRECTORY}:/playbook ${IMAGE_NAME} /bin/bash
```

This example assumes the following:
- a resource group already exists with access rights to create virtual machines
- the resource group contains a single vnet with a single subnet

### 2. Log into azure subcription
Ansible supports number of different methods for loggin in and authenticating with Azure.  This How-To uses the azure-cli to login interactively.
```
# log into azure subscription - interactive login
$ export AZURE_RESOURCE_GROUP=<existing-resource-group-name>
$ az login
```

### 3. Create an empty Ansible role with molecule
molecule provides an init function with defaults for various providers
```
# initialise a new role from a cookiecutter template
$ mkdir /playbook/roles
$ cd /playbook/roles
$ molecule init template --url https://www.github.com/datwiz/molecule-azure-role-template -r my-role
# provide answers to the prompt...
$ cd my-role
```
Check that the environment is working:
```
$ molecule list

# output should look similar to...
--> Validating schema /playbook/roles/my-role/molecule/default/molecule.yml.
Validation completed successfully.
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
my-role-bionic   azure          ansible             default          false      false
```

### 4. Spin up an Azure VM
Spin up a fresh VM to be used for infra-code development.
```
$ molecule create
$ molecule list
$ az vm list -o table -g ${AZURE_RESOURCE_GROUP}

# molecule provides a handy option for logging into the new VM
$ molecule login
```

There is now a fresh Ubuntu 18.04 virtual machine ready for infra-code development.  
For this How-To, a basic nginx server will be installed and verified.

### 5. Write a failing test
[Testinfra](https://testinfra.readthedocs.io/en/latest/) provides a pytest based framework for verifying server and infrastructure configuration.
Molecule then manages the execution of those testinfra tests.  The molecule template provides a starting point for crafting tests of your own.
For this tutorial, installation of the nginx service is verifed.
```
$ vi molecule/default/tests/test_default.py

# add the following Testinfra tests:
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
```

### 6. Execute the failing test
The ansible tasks needed to install and enable nginx have not yet been written, so the test should fail:
```
$ molecule verify
```
If the initial sample tests in `test_default.py` are kept, then 3 tests should fail and 2 tests pass.

### 7. Write a task to install nginx
Add a task to install nginx service.
```
$ vi tasks/main.yml

# add following ansible task
- name: install nginx as a service
  package:
    name: "nginx"
    state: present
```

### 8. Apply the role
Apply the role to the instance created via molecule.
```
$ molecule converge
```
The nginx pacakge should now be installed, both enabled and stated, and listening on port 80.  Note that the nginx instance will not be accessible from the Internet due
to the Azure network security rules only allowing ssh connections from the Internet.  The nginx instance can be confirmed manually by logging into the instance and
using `curl` to make a request to the nginx service.
```
$ molecule login

# from the login shell on the instance
$ curl http://localhost:80
# log out of the instance
$ exit

```

### 9. Execute the passing test
After applying the ansible task to the instance, the testinfra tests should now pass.
```
$ molecule verify
```
All 5 tests should now pass.

### 10. Cleanup
Now that the Ansible role works as defined in the test specification, the development environment can be cleaned up.
```
$ molecule destroy
$ molecule list
```
Molecule removes the Azure resources created to develop and test the configuration role.
Note that deletion may take a few minutes.

Finally, once done wth test/dev/refactor exit the contain environment.  If the container was started with the `--rm` switch, the container
will also be removed, leaving you with a clean workspace and newly minted ansible role with automated test cases.
```
$ exit
$ docker ps -a | grep molecule-azure
```

