#!/usr/bin/env bash
# Build the image and push it to a local registry that Docker Desktop Kubernetes can pull from.
# Port 5001 because macOS AirPlay Receiver occupies 5000.
set -euo pipefail

IMAGE=localhost:5001/external-sort:latest

docker start local-registry 2>/dev/null || docker run -d -p 5001:5000 --name local-registry registry:2
docker build -t "$IMAGE" "$(dirname "$0")/.."
docker push "$IMAGE"
