#!/usr/bin/env bash
# Deploy Kubernetes Dashboard and Metrics Server (run once)
set -euo pipefail
source "$(dirname "$0")/lib.sh"

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl apply -f "$K8S_DIR/dashboard-admin.yaml"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
