# ceradmin_ansible > awx

Configuration for running [AWX](https://github.com/ansible/awx) using [AWX Operator](https://github.com/ansible/awx-operator) and [K3s](https://github.com/k3s-io/k3s) on Nectar infrastructure.


## Installation

### System Preparation

The following steps are tested on Ubuntu 24.04.

Install requirements:

```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git make curl
```

Install k3s:

```
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```

Clone this repository:

```
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

### Create Local Docker Registry

Install Docker, configure the Docker environment (add registry and allow HTTP connections):

```
./registry/configure.sh
```

Deploy local docker registry:

```
kubectl create namespace registry
kubectl apply -k registry
```

### Create Ansible Image Builder

Install Pip and the Ansible builder:

```
sudo apt install python3-pip
pip install ansible-builder
```

Build the image:

```
cd ceradmin_ansible/awx/builder
$USER/.local/bin/ansible-builder build --tag awx.auckland-cer.cloud.edu.au:5000/awx-custom-image:latest --container-runtime=docker --verbosity 3
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
