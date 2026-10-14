#!/usr/bin/env bash
# Build the Docker image and push to the local registry (localhost:5001).
# Required because Docker Desktop Kubernetes uses a separate containerd image store.
# Port 5001 is used instead of 5000 because macOS AirPlay Receiver occupies 5000.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

IMAGE="localhost:5001/external-sort:latest"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if ! docker ps --format '{{.Names}}' | grep -q '^local-registry$'; then
  docker run -d -p 5001:5000 --restart=always --name local-registry registry:2
  ok "Started local registry on localhost:5001"
else
  ok "Local registry already running"
fi

docker build -t "$IMAGE" "$PROJECT_DIR"
docker push "$IMAGE"
ok "Image pushed: $IMAGE"
