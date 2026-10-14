#!/usr/bin/env bash
# Run everything end to end: build → generate data → benchmark (Windows/Git Bash)
# Usage: bash scripts/windows/run_all.sh [--sizes 1,2]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT="$(dirname "$SCRIPT_DIR")"

export BENCHMARK_SIZES="1 2 4 8"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sizes) BENCHMARK_SIZES="${2//,/ }"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

bash "$PARENT/02_build_and_load.sh"
bash "$PARENT/03_generate_data.sh"
bash "$SCRIPT_DIR/04_run_benchmarks.sh"
