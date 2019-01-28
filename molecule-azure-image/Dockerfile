FROM ubuntu:18.04

# install ansible, molecule, and azure-cli
COPY files/root/ /root/

RUN apt-get update && \
    apt-get install -y \
        curl \
        git \
        python-pip \
        software-properties-common \
        tree \
        vim && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ bionic main" && \
    apt-get update && \
    apt-get install -y \
        azure-cli && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -r /root/requirements.txt

# pip packages installed
#  ansible
#  ansible[azure]
#  molecule
#  molecule[azure]
#  testinfra

LABEL molecule-azure.ansible.version=2.7.6 \
      molecule-azure.azure-cli.version=2.0.55 \
      molecule-azure.molecule.version=2.19.0 \
      molecule-azure.testinfra.version=1.19.0

# ignore the collections.abc deprication warnings
ENV PYTHONWARNINGS="ignore:Using or importing the ABCs:DeprecationWarning"

WORKDIR /playbook
