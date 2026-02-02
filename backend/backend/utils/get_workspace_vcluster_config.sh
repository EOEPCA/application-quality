#!/bin/bash

# Retrieve a workspace vcluster kubeconfig from a secret and save it in a file.
#
# The script must receive the name of the namespace, the vcluster name, and the output file
#
# Example: sh get_workspace_vcluster_kubeconfig ws-alice default-vc /tmp/kubeconfig-ws-alice

workspace_name="$1"
cluster_name="$2"
file_name="$3"
namespace_name="${workspace_name}-${cluster_name}"
secret_name="${namespace_name}-kubeconfig"

echo "Retrieving the kubeconfig of vcluster ${cluster_name} in workspace ${workspace_name} ..."

echo "kubectl get secret ${secret_name} --namespace ${namespace_name} -o json | jq --raw-output '.data.config' | base64 --decode - > ${file_name}"
kubectl get secret ${secret_name} --namespace ${namespace_name} -o json | jq --raw-output '.data.config' | base64 --decode - > ${file_name}

echo "Successfully retrieved and stored the workspace vcluster kubeconfig in ${file_name}"