#!/usr/bin/env bash
# Run benchmark Jobs sequentially. Results written to /data/results.json on the PVC.
# Opens http://localhost:9090 when complete.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")/k8s"
source "$SCRIPT_DIR/lib.sh"

read -ra SIZES <<< "${BENCHMARK_SIZES:-1 2 4 8}"
NODE_GB=$(node_allocatable_gb)
read -ra SIZES <<< "$(filter_sizes "$NODE_GB" "${SIZES[@]}")"
[ ${#SIZES[@]} -eq 0 ] && { err "No sizes fit on this node (~${NODE_GB}GB allocatable)"; exit 1; }

kubectl apply -f "$K8S_DIR/results-server.yaml"

for SIZE in "${SIZES[@]}"; do
  JOB="benchmark-${SIZE}gb"
  echo "[ ${SIZE}GB ]"

  kubectl delete job "$JOB" -n sort-benchmark --ignore-not-found=true
  sleep 2
  kubectl apply -f "$K8S_DIR/job-${SIZE}gb.yaml"

  kubectl wait --for=condition=complete "job/$JOB" -n sort-benchmark --timeout=3600s 2>/dev/null || \
  kubectl wait --for=condition=failed   "job/$JOB" -n sort-benchmark --timeout=10s   2>/dev/null || true

  STATUS=$(kubectl get job "$JOB" -n sort-benchmark \
    -o jsonpath='{.status.conditions[0].type}' 2>/dev/null || echo "Unknown")
  [ "$STATUS" = "Failed" ] && warn "${SIZE}GB FAILED (OOMKilled?)" || ok "${SIZE}GB done"

  kubectl delete job "$JOB" -n sort-benchmark --ignore-not-found=true
  sleep 2
done

pkill -f "port-forward.*results-server" 2>/dev/null || true
sleep 1
kubectl port-forward svc/results-server 9090:8080 -n sort-benchmark &
sleep 2
open "http://localhost:9090" 2>/dev/null || xdg-open "http://localhost:9090" 2>/dev/null || true
printf "Results at http://localhost:9090\n"
wait
