# ceradmin_ansible > awx

Configuration for running [AWX](https://github.com/ansible/awx) using [AWX Operator](https://github.com/ansible/awx-operator) and [K3s](https://github.com/k3s-io/k3s) on Nectar infrastructure.


## Installation

### System Preparation

The following steps are tested on Ubuntu 24.04.

Install requirements:

```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git make curl ca-certificates python3-pip
```

Install k3s:

```
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```

Clone this repository:

```
cd ~
git clone https://github.com/UoA-eResearch/ceradmin_ansible.git
```

### Install AWX Operator

Deploy AWX Operator using config in `awx/operator`:

```
cd ceradmin_ansible/awx
kubectl create namespace awx
kubectl apply -k operator
```

### Install AWX

Create local directories to store data:

```
sudo mkdir -p /data/postgres-13
sudo mkdir -p /data/projects
sudo chmod 755 /data/postgres-13
sudo chown 1000:0 /data/projects
```

> Note: For deployment on Nectar, you can leverage the DNS Zones (found under Projects > DNS > Zones > Create record set) to create a subdomain.

Create self-signed TLS key pair:

```
AWX_HOST="awx.auckland-cer.cloud.edu.au"
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -out ./awx/tls.crt -keyout ./awx/tls.key -subj "/CN=${AWX_HOST}/O=${AWX_HOST}" -addext "subjectAltName = DNS:${AWX_HOST}"
```

Deploy AWX:

```
kubectl apply -k awx
```

### Install Docker

Remove any any existing Docker packages:

```
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove -y $pkg; done
```

Install Docker Engine:

```
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
```

### Create Local Docker Registry

Add the Docker registry:

```
sudo rm -f /etc/rancher/k3s/registries.yaml
echo 'mirrors:' | sudo tee -a /etc/rancher/k3s/registries.yaml
echo ' "awx.auckland-cer.cloud.edu.au:5000":' | sudo tee -a /etc/rancher/k3s/registries.yaml
echo '   endpoint:' | sudo tee -a /etc/rancher/k3s/registries.yaml
echo '     - "http://awx.auckland-cer.cloud.edu.au:5000"' | sudo tee -a /etc/rancher/k3s/registries.yaml
```

Allow HTTP registry:

```
sudo rm -f /etc/docker/daemon.json
echo '{ "insecure-registries":["awx.auckland-cer.cloud.edu.au:5000"] }' | sudo tee -a /etc/docker/daemon.json
```

Include the registry in the Docker configuration:

```
sudo rm -f /etc/default/docker
echo 'DOCKER_OPTS="--config-file=/etc/docker/daemon.json"' | sudo tee -a /etc/default/docker
```

Stop and start the Docker service:

```
sudo systemctl stop docker.service
sudo systemctl start docker.service
```

Deploy local docker registry:

```
kubectl create namespace registry
kubectl apply -k registry
```

### Create Ansible Image Builder

Install Pip and the Ansible builder:

```
pip install ansible-builder
```

Build the image:

```
cd ~/ceradmin_ansible/awx/builder
/home/$USER/.local/bin/ansible-builder build --tag awx.auckland-cer.cloud.edu.au:5000/awx-custom-image:latest --container-runtime=docker --verbosity 3
```

Push the Docker image to the local registry:

```
docker push awx.auckland-cer.cloud.edu.au:5000/awx-custom-image
```

## Helpful Commands

Check logs for a specific deployment:

```
kubectl -n awx logs -f deployments/awx-operator-controller-manager
kubectl -n awx logs -f deployment.apps/awx-web
```

Check `awx` namespace for resources:

```
kubectl -n awx get awx,all,ingress,secrets
```

Get a secret:

```
kubectl get secrets -n awx awx-admin-password -o jsonpath='{.data}'
echo "DATA" | base64 -d
```
