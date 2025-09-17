#!/bin/env sh

set -e

kubectl config set-cluster in-cluster \
  --server="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}" \
  --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  --embed-certs=true
kubectl config set-credentials in-cluster-user --token=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
kubectl config set-context in-cluster --cluster=in-cluster --user=in-cluster-user
kubectl config use-context in-cluster

if [ -z "$SHARED_VCLUSTER_NAME" ] || [ -z "$SHARED_VCLUSTER_NAMESPACE" ]; then
  echo "Could not connect to vcluster: SHARED_VCLUSTER_NAME or SHARED_VCLUSTER_NAMESPACE is not set."
  exit 0
fi

echo "Creating vcluster $SHARED_VCLUSTER_NAME ..."
set +e
vcluster create $SHARED_VCLUSTER_NAME -n $SHARED_VCLUSTER_NAMESPACE \
  --set=networking.replicateServices.fromHost[0].from=$HOST_CLUSTER_SERVICE \
  --set=networking.replicateServices.fromHost[0].to=$SHARED_VCLUSTER_SERVICE \
  --connect=false
set -e

echo "Connecting to vcluster $SHARED_VCLUSTER_NAME ..."
vcluster connect $SHARED_VCLUSTER_NAME -n $SHARED_VCLUSTER_NAMESPACE --server=$SHARED_VCLUSTER_NAME.$SHARED_VCLUSTER_NAMESPACE
