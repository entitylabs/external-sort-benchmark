#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
K8S_DIR="$(dirname "$SCRIPT_DIR")/k8s"

kubectl apply -f "$K8S_DIR/namespace.yaml" -f "$K8S_DIR/pvc.yaml"
kubectl delete job generate-data -n sort-benchmark --ignore-not-found=true
kubectl apply -f "$K8S_DIR/generate-job.yaml"

POD=""
for i in $(seq 1 20); do
  POD=$(kubectl get pods -n sort-benchmark -l job-name=generate-data \
    -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
  [ -n "$POD" ] && break
  sleep 3
done
[ -z "$POD" ] && { err "Generator pod did not appear"; exit 1; }

kubectl logs -f "$POD" -n sort-benchmark || true
kubectl wait --for=condition=complete job/generate-data -n sort-benchmark --timeout=3600s
ok "Dataset ready"
