# Infracode using molecule on Azure

## An all Python stack for infracode
Ansible with [molecule](https://molecule.readthedocs.io/) delivers an all python infra-code stack
for developing and testing infrastructure configurations.  

test-kitchen works with ansible and azure, but a ruby environment and at least a smattering of ruby coding skills.
molecule provides a similar red-green development cycle to test-kitchen, but without the need to step outside
of the familiar python environment.

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

### molecule on Azure
The default templates for the azure driver are geared towards a personal tutorial environment, where
you own a subscription and have the rights to create resource groups and networks with public IP
address connectivity.
In an enterprise environment, access rights is often more restrictive.
This tutorial is greared towards using ansible and molecule in an enterprise context, where an
infracode developer has access to create VM's in designated environments, but restricted in the creation
of resource groups or networks.


## Setting up a working environment
Python virtualenv or docker container environment

this tutorial uses makes use a a containerised development environment.

### Create a local working environment docker image
Setup working environment using a docker image with ansible, molecule, and the azure-cli installed

```
export IMAGE_BUILD_DIRECTORY=./molecule-azure-image
export IMAGE_NAME=molecule-azure:latest
export ANSIBLE_PLAYBOOK_DIRECTORY=$(pwd)/playbook

docker build -t ${IMAGE_NAME} ${IMAGE_BUILD_DIRECTORY}
```

## Setup a working environment
```
# start working environment container with a working directory of /playbook
docker run -it --name molecule-azure -v ${ANSIBLE_PLAYBOOK_DIRECTORY}:/playbook ${IMAGE_NAME} /bin/bash

# log into azure subscription - interactive login
az login

# initialise a new role
mkdir /playbook/roles
cd roles
molecule init role --role-name my-role --driver-name azure
cd my-role
```

```
$ molecule list

--> Validating schema /playbook/roles/my-role/molecule/default/molecule.yml.
Validation completed successfully.
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         docker         ansible             default          false      false
root@8db44c1d93f3:/playbook/roles/my-role#
```

## Setup to use molecule on azure with existing resources
### Resources
```
resource_group_name;
location:
virtual_network_name:
subnet_name:
vm_size:
image:
  offer:
  publisher:
  sku:
  version: 
```
