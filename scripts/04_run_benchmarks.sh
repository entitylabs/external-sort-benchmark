#!/usr/bin/env bash
# Run the benchmark jobs one after another, then serve results on http://localhost:9090
set -euo pipefail
source "$(dirname "$0")/lib.sh"

kubectl apply -f "$K8S_DIR/results-server.yaml"

for SIZE in ${BENCHMARK_SIZES:-1 2 4 8}; do
  JOB="benchmark-${SIZE}gb"
  kubectl delete job "$JOB" -n "$NS" --ignore-not-found
  kubectl apply -f "$K8S_DIR/job-${SIZE}gb.yaml"
  wait_for_job "$JOB" || echo "${SIZE}GB failed"
done

stop_results_forward
kubectl port-forward svc/results-server 9090:8080 -n "$NS" &
sleep 2
open_url http://localhost:9090
wait
