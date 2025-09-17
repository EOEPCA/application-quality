import logging
import os
import requests


WORKSPACE_API_SERVICE_URL = os.getenv(
    "WORKSPACE_API_SERVICE_URL",
    "http://workspace-api.workspace.svc.cluster.local:8080",
)

logger = logging.getLogger(__name__)


def get_vcluster_config(ws_name: str) -> tuple([dict, str]):
    logger.info("Fetching kubeconfig for workspace %s", ws_name)
    ws_info = requests.get(f"{WORKSPACE_API_SERVICE_URL}/workspaces/{ws_name}")
    logger.debug("HTTP status code: %s", ws_info.status_code)
    if ws_info.status_code != 200:
        logger.error("Error: HTTP status code is %s", ws_info.status_code)
        return "", "error"
    # The Workspace API always returns a dict, even if the workspace does not exist
    # If it doesn't exist, the status is "unknown" and the other values are either None or []
    ws_info_dict = ws_info.json()
    if ws_info_dict.get("status", "unknown") in [None, "unknown"]:
        logger.error("Error: workspace %s not found", ws_name)
        return "", "error"
    if not ws_info_dict.get("status", None) == "ready":
        logger.error("Error: workspace %s is not ready", ws_name)
        return "", "error"
    # logger.debug(f"Workspace status: {}")
    ws_cluster_dict = ws_info_dict.get("cluster", {})
    if ws_cluster_dict is None:
        logger.error("Error: workspace %s has no cluster information", ws_name)
        return "", "error"
    ws_cluster_status = ws_cluster_dict.get("status", None)
    ws_cluster_config = ws_cluster_dict.get("config", None)
    logger.debug("Workspace cluster status: %s", ws_cluster_status)
    if not ws_cluster_status == "active":
        # Other possible statuses: suspended, disabled
        logger.info("Cluster not active => Must resume or active it now (TODO)")
        return "", ws_cluster_status

    return ws_cluster_config, ws_cluster_status


def get_vcluster_config_file(ws_name: str) -> str:

    vcluster_config, vcluster_status = get_vcluster_config(ws_name)
    logger.debug("Workspace vCluster status: %s", vcluster_status)
    logger.debug("Workspace vCluster config: %s ...", vcluster_config[0:100])
    kubeconfig_file = "/tmp/kubeconfig-" + ws_name
    with open(kubeconfig_file, "w") as f:
        f.write(vcluster_config)
    return kubeconfig_file
