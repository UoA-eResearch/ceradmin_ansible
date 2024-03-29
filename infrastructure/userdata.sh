#!/bin/bash

# Update system
apt-get update
DEBIAN_FRONTEND=noninteractive DEBIAN_PRIORITY=critical apt-get --yes --quiet --option Dpkg::Options::=--force-confold --option Dpkg::Options::=--force-confdef upgrade

# Install packaged
apt-get install -y git make curl python3-pip docker.io

# Install k3s
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

# Make storage folders
mkdir -p /data/postgres-13
mkdir -p /data/projects
chmod 755 /data/postgres-13
chown 1000:0 /data/projects

# Add user to Docker group
sudo usermod -aG docker ubuntu

# Add Docker Registry entry
rm -f /etc/rancher/k3s/registries.yaml
echo 'mirrors:' | tee -a /etc/rancher/k3s/registries.yaml
echo ' "awx.auckland-cer.cloud.edu.au:5000":' | tee -a /etc/rancher/k3s/registries.yaml
echo '   endpoint:' | tee -a /etc/rancher/k3s/registries.yaml
echo '     - "http://awx.auckland-cer.cloud.edu.au:5000"' | tee -a /etc/rancher/k3s/registries.yaml

# Allow HTTP for local Docker registry
rm -f /etc/docker/daemon.json
echo '{ "insecure-registries":["awx.auckland-cer.cloud.edu.au:5000"] }' | tee -a /etc/docker/daemon.json

# Include the local registry in the Docker configuration
rm -f /etc/default/docker
echo 'DOCKER_OPTS="--config-file=/etc/docker/daemon.json"' | tee -a /etc/default/docker

# Stop and start the Docker service
systemctl stop docker.service
systemctl start docker.service

# Make a new directory to store everything
WORKDIR="/data/"
cd "$WORKDIR" || exit

# Clone the repo
git clone https://github.com/UoA-eResearch/ceradmin_ansible.git

# TODO: when done remove change branch
git config --global --add safe.directory $WORKDIR/ceradmin_ansible
cd $WORKDIR/ceradmin_ansible || exit
git checkout update-awx-k3-config

# OPERATOR
cd $WORKDIR/ceradmin_ansible/awx/ || exit
kubectl create namespace awx
kubectl apply -k operator

sleep 30

# AWX
cd $WORKDIR/ceradmin_ansible/awx/ || exit
AWX_HOST="awx.auckland-cer.cloud.edu.au"
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -out ./awx/tls.crt -keyout ./awx/tls.key -subj "/CN=${AWX_HOST}/O=${AWX_HOST}" -addext "subjectAltName = DNS:${AWX_HOST}"
kubectl apply -k awx

sleep 60

# REGISTRY
cd $WORKDIR/ceradmin_ansible/awx/ || exit
kubectl create namespace registry
kubectl apply -k registry

sleep 300

# BUILDER
cd $WORKDIR/ceradmin_ansible/awx/builder || exit
pip install ansible-builder
ansible-builder build --tag awx.auckland-cer.cloud.edu.au:5000/awx-custom-image:latest --container-runtime=docker --verbosity 3
docker push awx.auckland-cer.cloud.edu.au:5000/awx-custom-image
