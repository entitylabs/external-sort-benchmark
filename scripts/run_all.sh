#!/usr/bin/env bash
# Build, generate data, and run benchmarks
# Usage: bash scripts/run_all.sh [--sizes 1,2]
set -euo pipefail
DIR="$(dirname "$0")"
source "$DIR/lib.sh"

[[ "${1:-}" == --sizes ]] && export BENCHMARK_SIZES="${2//,/ }"

# Start clean: removes old jobs, results and data (waits until fully gone)
kubectl delete namespace "$NS" --ignore-not-found

bash "$DIR/02_build_and_load.sh"
bash "$DIR/03_generate_data.sh"
bash "$DIR/04_run_benchmarks.sh"
