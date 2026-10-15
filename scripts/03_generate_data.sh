#!/usr/bin/env bash
# Generate the input CSV on the shared volume
set -euo pipefail
source "$(dirname "$0")/lib.sh"

kubectl apply -f "$K8S_DIR/namespace.yaml" -f "$K8S_DIR/pvc.yaml"
kubectl delete job generate-data -n "$NS" --ignore-not-found
kubectl apply -f "$K8S_DIR/generate-job.yaml"
wait_for_job generate-data
