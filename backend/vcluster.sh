#!/bin/env sh

set -e

kubectl config set-cluster in-cluster \
  --server="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}" \
  --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  --embed-certs=true
kubectl config set-credentials in-cluster-user --token=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
kubectl config set-context in-cluster --cluster=in-cluster --user=in-cluster-user
kubectl config use-context in-cluster

if [ -z "$VCLUSTER_NAME" ] || [ -z "$VCLUSTER_NAMESPACE" ]; then
  echo "Could not connect to vcluster: VCLUSTER_NAME or VCLUSTER_NAMESPACE is not set."
  exit 0
fi

if vcluster list | grep -q "^$VCLUSTER_NAME\s"; then
  vcluster create $VCLUSTER_NAME -n $VCLUSTER_NAMESPACE \
    --set=networking.replicateServices.fromHost[0].from=$HOST_CLUSTER_SERVICE \
    --set=networking.replicateServices.fromHost[0].to=$VCLUSTER_SERVICE \
    --connect=false
fi

vcluster connect $VCLUSTER_NAME -n $VCLUSTER_NAMESPACE --server=$VCLUSTER_NAME.$VCLUSTER_NAMESPACE
