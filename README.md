# Test Driven Infrastructure with Ansiblei, Molecule, and Azure
[Test Driven Infrastructure and Test Automation with Ansible, Molecule, and Azure](https://www.cloudywithachanceofbigdata.com/test-driven-infrastructure-and-test-automation-with-ansible-molecule-and-azure/)

This tutorial demonstrates how to use Molecule with Azure to develop and test an individual Ansible
role following the the red/green/refactor infracode workflow, which can be generalised as:
* Red - write a failing infrastructure test
* Green - write the Ansible tasks needed to pass the test
* Refactor - repeat the process

The steps required for this tutorial are as follows:

## Azure setup
Ensure there is an existing Azure Resource Group that will be used for infracode development and testing.
Within the resource group, ensure there is a single virtual network (vnet) with a single subnet. Ansible
will use these for the default network setup.

## Setup a working environment
There are a number of options for setting up a python environment for Ansible and Molecule, including
Python virtualenv or a Docker container environment.

## Create Docker image for Ansible+Molecule+Azure
This tutorial uses a Docker container environment.  A Dockerfile for the image can be found in
`./molecule-azure-image/Dockerfile`  The image sets up a sane Python3 environment with `ansible`,
`ansible[azure]`, and `molecule` pip modules installed.
```
$ export IMAGE_BUILD_DIRECTORY=./molecule-azure-image
$ export IMAGE_NAME=molecule-azure:latest
$ docker build -t ${IMAGE_NAME} ${IMAGE_BUILD_DIRECTORY}
```

## Create a Docker workspace
Setup working environment using a docker image with Ansible, Molecule, and the azure-cli installed.
```
$ export ANSIBLE_PLAYBOOK_DIRECTORY=$(pwd)/playbook
$ docker run -it --rm --name molecule-azure -v ${ANSIBLE_PLAYBOOK_DIRECTORY}:/playbook ${IMAGE_NAME} /bin/bash
```
This example assumes the following:
- a resource group already exists with access rights to create virtual machines; and
- the resource group contains a single vnet with a single subnet

## Log into an Azure subcription
Ansible supports a number of different methods for authenticating with Azure.  This example uses the
azure-cli to login interactively.
```
# log into azure subscription - interactive login
$ export AZURE_RESOURCE_GROUP=<existing-resource-group-name>
$ az login
```

## Create an empty Ansible role with Molecule
Molecule provides an init function with defaults for various providers. The `molecule-azure-role-template`
creates an empty role with scaffolding for Azure.
```
# initialise a new role from a cookiecutter template
$ mkdir /playbook/roles
$ cd /playbook/roles
$ molecule init template --url https://www.github.com/datwiz/molecule-azure-role-template -r my-role
# provide answers to the prompt...
$ cd my-role
```
Check that the environment is working by running the following code:
```
$ molecule list
```
The output should look similar to...
```
--> Validating schema /playbook/roles/my-role/molecule/default/molecule.yml.
Validation completed successfully.
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
my-role-bionic   azure          ansible             default          false      false
```

## Spin up an Azure VM
Spin up a fresh VM to be used for infra-code development.
```
$ molecule create
$ molecule list
$ az vm list -o table -g ${AZURE_RESOURCE_GROUP}
```
Molecule provides a handy option for logging into the new VM:
```
$ molecule login
```
There is now a fresh Ubuntu 18.04 virtual machine ready for infra-code development.  
For this example, a basic Nginx server will be installed and verified.

## Write a failing test
[Testinfra](https://testinfra.readthedocs.io/en/latest/) provides a pytest based framework for verifying server and infrastructure configuration.
Molecule then manages the execution of those testinfra tests.  The molecule template provides a
starting point for crafting tests of your own.  For this tutorial, installation of the nginx service
is verifed.
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

## Execute the failing test
The ansible task needed to install and enable nginx has not yet been written, so the test should fail:
```
$ molecule verify
```
If the initial sample tests in `test_default.py` are kept, then 3 tests should fail and 2 tests should pass.

## Write a task to install nginx
Add a task to install the nginx service.
```
$ vi tasks/main.yml

# add following ansible task
- name: install nginx as a service
  package:
    name: "nginx"
    state: present
```

## Apply the role
Apply the role to the instance created using Molecule.
```
$ molecule converge
```
The nginx pacakge should now be installed, both enabled and stated, and listening on port 80.  Note
that the nginx instance will not be accessible from the Internet due to the Azure network security
rules.  The nginx instance can be confirmed manually by logging into the instance and using `curl`
to make a request to the nginx service.
```
$ molecule login

# from the login shell on the instance
$ curl http://localhost:80
# log out of the instance
$ exit

```

## Execute the passing test
After applying the ansible task to the instance, the testinfra tests should now pass.
```
$ molecule verify
```
All 5 tests should now pass.

## Cleanup
Now that the Ansible role works as defined in the test specification, the development environment
can be cleaned up.
```
$ molecule destroy
$ molecule list
```
Molecule removes the Azure resources created to develop and test the configuration role.
Note that deletion may take a few minutes.

Finally, once you are done, exit the container environment.  If the container was started with the
`--rm` switch, the container will also be removed, leaving you with a clean workspace and newly
minted ansible role with automated test cases.
```
$ exit
$ docker ps -a | grep molecule-azure
```
