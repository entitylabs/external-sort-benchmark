#!/usr/bin/env bash
# Deploy Kubernetes Dashboard and Metrics Server (run once).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")/k8s"
source "$SCRIPT_DIR/lib.sh"

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl apply -f "$K8S_DIR/dashboard-admin.yaml"

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system \
  --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]' \
  2>/dev/null || true

kubectl rollout status deployment/kubernetes-dashboard -n kubernetes-dashboard --timeout=120s
ok "Dashboard ready — run: bash scripts/05_open_dashboard.sh"
