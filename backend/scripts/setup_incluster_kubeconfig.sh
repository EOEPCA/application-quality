#!/bin/bash

# Configure kubectl for in-cluster access.
# Use the environment variables and files provided by the
# Kubernetes ServiceAccount mechanism to set up a new context named 'in-cluster'.

echo "Generating kubeconfig for in-cluster access ..."

# 1. Set up the cluster details (Server and CA)
kubectl config set-cluster in-cluster \
  --server="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}" \
  --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  --embed-certs=true

# 2. Set up the credentials using the mounted ServiceAccount token
kubectl config set-credentials in-cluster-user --token=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)

# 3. Define the context, linking the cluster and user
kubectl config set-context in-cluster --cluster=in-cluster --user=in-cluster-user

# 4. Activate the new context
kubectl config use-context in-cluster

echo "Successfully created kubeconfig with 'in-cluster' context."
