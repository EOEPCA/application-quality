#!/bin/env sh

set -e

if [ -z "$SHARED_VCLUSTER_NAME" ] || [ -z "$SHARED_VCLUSTER_NAMESPACE" ]; then
  echo "Cannot use a shared vcluster: SHARED_VCLUSTER_NAME or SHARED_VCLUSTER_NAMESPACE is not set."
  exit 0
fi

echo "Creating vcluster $SHARED_VCLUSTER_NAME ..."
set +e
vcluster create $SHARED_VCLUSTER_NAME -n $SHARED_VCLUSTER_NAMESPACE \
  --set=networking.replicateServices.fromHost[0].from=$HOST_CLUSTER_SERVICE \
  --set=networking.replicateServices.fromHost[0].to=$SHARED_VCLUSTER_SERVICE \
  --connect=false
set -e

# echo "Connecting to vcluster $SHARED_VCLUSTER_NAME ..."
# vcluster connect $SHARED_VCLUSTER_NAME -n $SHARED_VCLUSTER_NAMESPACE --server=$SHARED_VCLUSTER_NAME.$SHARED_VCLUSTER_NAMESPACE

echo "Created vcluster $SHARED_VCLUSTER_NAME"
