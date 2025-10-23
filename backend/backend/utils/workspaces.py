import logging
import os
import requests
import subprocess
import sys


WORKSPACE_API_SERVICE_URL = os.getenv(
    "WORKSPACE_API_SERVICE_URL",
    "http://workspace-api.workspace.svc.cluster.local:8080",
)

logger = logging.getLogger(__name__)


def get_vcluster_config(ws_name: str) -> tuple([dict, str]):
    logger.info("Fetching kubeconfig for workspace %s", ws_name)
    logger.debug("HTTP request URL: %s/workspaces/%s", WORKSPACE_API_SERVICE_URL, ws_name)
    ws_info = requests.get(f"{WORKSPACE_API_SERVICE_URL}/workspaces/{ws_name}", timeout=10)
    logger.debug("HTTP status code: %s", ws_info.status_code)
    if ws_info.status_code != 200:
        logger.error("Error: HTTP status code is %s", ws_info.status_code)
        return None, "error"
    # The Workspace API always returns a dict, even if the workspace does not exist
    # If the workspace does not exist, the status is "unknown" and the other values are either None or []
    ws_info_dict = ws_info.json()
    if ws_info_dict.get("status", "unknown") in [None, "unknown"]:
        logger.error("Error: workspace %s not found", ws_name)
        return None, "error"
    if not ws_info_dict.get("status", None) == "ready":
        logger.error("Error: workspace %s is not ready", ws_name)
        return None, "error"
    logger.info("Workspace %s is ready", ws_name)
    # logger.debug(f"Workspace status: {}")
    ws_cluster_dict = ws_info_dict.get("cluster", None)
    if ws_cluster_dict is None or ws_cluster_dict == {}:
        logger.error("Error: workspace %s has no cluster information", ws_name)
        return None, "error"
    ws_cluster_status = ws_cluster_dict.get("status", None)
    ws_cluster_config = ws_cluster_dict.get("config", None)
    logger.debug("Workspace cluster status: %s", ws_cluster_status)
    if not ws_cluster_status == "active":
        # Other possible statuses: suspended, disabled
        logger.info("Cluster not active => Must resume or active it now (TODO)")
        return "", ws_cluster_status

    return ws_cluster_config, ws_cluster_status


def get_vcluster_config_file(ws_name: str, vc_name: str = "default-vc") -> str:

    config_file = "/tmp/kubeconfig-" + ws_name
    # Get the vcluster config using the Workspace API
    vcluster_config, vcluster_status = get_vcluster_config(ws_name)
    if vcluster_config:
        # Save the kubeconfig content in a file
        logger.debug("Workspace vCluster status: %s", vcluster_status)
        logger.debug("Workspace vCluster config: %s ...", vcluster_config[0:100])
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(vcluster_config)
        return config_file

    # Alternatively, try to get the vcluster config from a Workspace secret
    cwd = os.path.abspath(os.path.dirname(__file__))
    #cwd = "/app/backend/utils"
    script = f"{cwd}/get_workspace_vcluster_config.sh"
    cmd = ["/usr/bin/sh", script, ws_name, vc_name, config_file]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", e.stderr.strip())
        raise ValueError("Error: could not obtain vcluster: %s", e.stderr.strip())
    logger.debug("Stdout: %s", result.stdout)
    logger.debug("Stderr: %s", result.stderr)
    # Return the name of the file that contains the kubeconfig
    return config_file