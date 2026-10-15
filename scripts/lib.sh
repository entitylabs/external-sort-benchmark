#!/usr/bin/env bash
# Shared helpers for benchmark scripts

NS=sort-benchmark
K8S_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../k8s" && pwd)"

# Block until the job finishes; non-zero exit if it failed
wait_for_job() {

  local status
  while true; do
    status=$(kubectl get job "$1" -n "$NS" -o jsonpath='{.status.succeeded}/{.status.failed}')
    [[ $status == 1/* ]] && return 0
    [[ $status == */1 ]] && return 1
    sleep 5
  done
}

is_windows() {

  case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) return 0 ;; *) return 1 ;; esac
}

stop_results_forward() {

  if is_windows; then
    powershell.exe -NoProfile -Command \
      "Get-CimInstance Win32_Process -Filter \"Name='kubectl.exe'\" | Where-Object { \$_.CommandLine -like '*port-forward*results-server*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" \
      2>/dev/null || true
  else
    pkill -f "port-forward.*results-server" || true
  fi
}

open_url() {
  
  if is_windows; then
    cmd.exe /c start "" "$1" || true
  else
    open "$1" 2>/dev/null || xdg-open "$1" || true
  fi
}
