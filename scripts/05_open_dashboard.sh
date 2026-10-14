#!/usr/bin/env bash
# Print a login token and start kubectl proxy for the Kubernetes Dashboard.
set -euo pipefail

TOKEN=$(kubectl -n kubernetes-dashboard create token admin-user)

echo "URL:   http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
echo "Token: $TOKEN"
echo ""
echo "Starting kubectl proxy (Ctrl+C to stop)..."
kubectl proxy
