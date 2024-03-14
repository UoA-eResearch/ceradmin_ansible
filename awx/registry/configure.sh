#!/bin/bash


# Install Docker
sudo apt install docker.io
sudo usermod -aG docker "$USER"

# Add Docker Registry
sudo rm -f /etc/rancher/k3s/registries.yaml
echo 'mirrors:' | sudo tee -a /etc/rancher/k3s/registries.yaml
echo ' "awx.auckland-cer.cloud.edu.au:5000":' | sudo tee -a /etc/rancher/k3s/registries.yaml
echo '   endpoint:' | sudo tee -a /etc/rancher/k3s/registries.yaml
echo '     - "http://awx.auckland-cer.cloud.edu.au:5000"' | sudo tee -a /etc/rancher/k3s/registries.yaml

# Allow HTTP registry
sudo rm -f /etc/docker/daemon.json
echo '{ "insecure-registries":["awx.auckland-cer.cloud.edu.au:5000"] }' | sudo tee -a /etc/docker/daemon.json

# Include the registry in the Docker configuration
sudo rm -f /etc/default/docker
echo 'DOCKER_OPTS="--config-file=/etc/docker/daemon.json"' | sudo tee -a /etc/default/docker

# Stop and start the Docker service
sudo systemctl stop docker.service
sudo systemctl start docker.service
