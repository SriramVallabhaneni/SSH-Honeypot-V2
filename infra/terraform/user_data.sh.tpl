#!/bin/bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y docker.io git curl

systemctl enable docker
systemctl start docker

usermod -aG docker ubuntu

# Install k3s
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh -

# Wait for k3s
until systemctl is-active --quiet k3s; do
  sleep 5
done

# Kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

mkdir -p /home/ubuntu/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
chown -R ubuntu:ubuntu /home/ubuntu/.kube
chmod 600 /home/ubuntu/.kube/config

# Verify cluster is responding
until kubectl get nodes >/dev/null 2>&1; do
  sleep 5
done

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

mkdir -p /opt
cd /opt

if [ ! -d "${app_dir}" ]; then
  git clone ${repo_url} ${app_dir}
else
  cd ${app_dir}
  git pull
fi

git config --system --add safe.directory ${app_dir}

cd ${app_dir}

cp deploy/k8s/config/secret.example.yaml \
   deploy/k8s/config/secret.yaml

sed -i "s/change-me/${postgres_password}/g" \
  deploy/k8s/config/secret.yaml

# Build image
docker build -t ssh-honeypot:local .

# Import image into k3s
docker save ssh-honeypot:local | k3s ctr images import -

# Deploy application
KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply \
  -f deploy/k8s/namespace.yaml

KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply \
  -f deploy/k8s/config/configmap.yaml

KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply \
  -f deploy/k8s/config/secret.yaml

KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply \
  -f deploy/k8s/postgres/

KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply \
  -f deploy/k8s/honeypot/

# Monitoring
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts

helm repo update

KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm upgrade --install monitoring \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f deploy/k8s/monitoring/values.yaml \
  --timeout 10m

# ServiceMonitor
KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply \
  -f deploy/k8s/monitoring/honeypot-servicemonitor.yaml