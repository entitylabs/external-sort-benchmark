#!/usr/bin/env bash
# Shared helpers for benchmark scripts

ok()   { printf "\033[0;32m[ok] %s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m[warn] %s\033[0m\n" "$*"; }
err()  { printf "\033[0;31m[err] %s\033[0m\n" "$*" >&2; }

parse_mem_to_gb() {
  local raw="$1"
  if [[ "$raw" =~ ^([0-9]+)Gi$ ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$raw" =~ ^([0-9]+)Mi$ ]]; then
    echo $(( ${BASH_REMATCH[1]} / 1024 ))
  elif [[ "$raw" =~ ^([0-9]+)Ki$ ]]; then
    echo $(( ${BASH_REMATCH[1]} / 1024 / 1024 ))
  elif [[ "$raw" =~ ^([0-9]+)$ ]]; then
    echo $(( ${BASH_REMATCH[1]} / 1024 / 1024 / 1024 ))
  else
    echo "6"
  fi
}

node_allocatable_gb() {
  local raw
  raw=$(kubectl get nodes -o jsonpath='{.items[0].status.allocatable.memory}' 2>/dev/null || echo "6Gi")
  parse_mem_to_gb "$raw"
}

filter_sizes() {
  local node_gb="$1"; shift
  local runnable=()
  for s in "$@"; do
    if (( s >= node_gb )); then
      warn "${s}GB pod won't fit — node has ~${node_gb}GB. Increase Docker Desktop memory." >&2
    else
      runnable+=("$s")
    fi
  done
  echo "${runnable[@]}"
}
