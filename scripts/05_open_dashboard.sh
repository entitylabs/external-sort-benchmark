#!/usr/bin/env bash
# Print a login token and start kubectl proxy for the Kubernetes Dashboard
set -euo pipefail

echo "URL:   http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
echo "Token: $(kubectl -n kubernetes-dashboard create token admin-user)"
kubectl proxy
