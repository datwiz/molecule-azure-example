# Using molecule on Azure

## molecule with playbooks and roles
### molecule with roles

### molecule with playbooks

## Setting up a working environment
Python virtual environment or docker container

### Create a local working environment docker image
Setup working environment using a docker image with ansible, molecule, and the azure-cli installed

```
export MOLECULE_IMAGE_BUILD_DIRECTORY=./molecule-azure-image
export MOLECULE_IMAGE=molecule-azure:latest

docker build -t ${MOLECULE_IMAGE} ${MOLECULE_IMAGE_BUILD_DIRECTORY}
```

## Setup a working environment
```
# start working environment container with a working directory of /playbook
export ANSIBLE_PLAYBOOK_DIRECTORY=$(pwd)/playbook
docker run -it --name molecule-azure -v ${ANSIBLE_PLAYBOOK_DIRECTORY}:/playbook ${MOLECULE_IMAGE} /bin/bash

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
