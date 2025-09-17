import logging
import os

from json.decoder import JSONDecodeError
from kubernetes import config

from backend.models import PipelineRun
from backend.utils.workspaces import get_vcluster_config_file
from pycalrissian.context import CalrissianContext
from pycalrissian.execution import CalrissianExecution
from pycalrissian.job import CalrissianJob
from .tools import getenv_bool


AQBB_STORAGECLASS = os.getenv("AQBB_STORAGECLASS", "standard")
AQBB_VOLUMESIZE = os.getenv("AQBB_VOLUMESIZE", "5Gi")
AQBB_CALRISSIANIMAGE = os.getenv(
    "AQBB_CALRISSIANIMAGE",
    "nexus.spaceapplications.com/repository/docker-eoepca/calrissian:0.18.1"
)
AQBB_MAXCORES = os.getenv("AQBB_MAXCORES", "2")
AQBB_MAXRAM = os.getenv("AQBB_MAXRAM", "2Gi")
AQBB_SECRET = os.getenv("AQBB_SECRET", None)
# Create a ServiceAccount for Calrissian with the right roles and use it here
AQBB_SERVICEACCOUNT = os.getenv("AQBB_SERVICEACCOUNT", None)
# Backend service replicated in the vcluster (for reports storage)
BACKEND_SERVICE_HOST = os.getenv(
    "BACKEND_SERVICE_HOST",
    "backend-service.default.svc.cluster.local"
)
BACKEND_SERVICE_PORT = os.getenv("BACKEND_SERVICE_PORT", "80")
SONARQUBE_SERVER = os.getenv(
    "SONARQUBE_SERVER",
    "application-quality-sonarqube-sonarqube.application-quality-sonarqube.svc.cluster.local:9000"
)
SONARQUBE_TOKEN = os.getenv("SONARQUBE_TOKEN")

WORKSPACE_VCLUSTER_ENABLED = getenv_bool("WORKSPACE_VCLUSTER_ENABLED", False)
WORKSPACE_VCLUSTER_REQUIRED = getenv_bool("WORKSPACE_VCLUSTER_REQUIRED", False)
SHARED_VCLUSTER_ENABLED = getenv_bool("SHARED_VCLUSTER_ENABLED", False)
SHARED_VCLUSTER_REQUIRED = getenv_bool("SHARED_VCLUSTER_REQUIRED", False)

PUBLIC_URL = os.getenv("PUBLIC_URL", None)

logger = logging.getLogger(__name__)


def run_workflow(
    parameters: dict,
    run_id: int,
    cwl: dict,
    username: str,
) -> dict:
    pipeline_run = PipelineRun.objects.get(id=run_id)

    '''
    """
    Create the image pull secrets
    """
    username = ""
    password = ""


    """
    Make a string with the username and the password,
    turn it into a string literal (encode()),
    encode the literal in base 64,
    turn the encoded string literal back into a regular string (decode()).
    """
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()

    secret_config = {
        "auths": {
            "registry.gitlab.com": {"auth": ""},
            "https://index.docker.io/v1/": {"auth": ""},
        }
    }
    '''

    logger.debug("Executing workflow for user %s", username)

    kubeconfig = os.getenv("KUBECONFIG", None)

    if kubeconfig:  # Only useful for debugging purposes
        try:
            config.load_kube_config(config_file=kubeconfig)
            logger.debug("Config file loaded successfully.")
        except Exception as e:
            logger.error("Failed to load config file: %s", e)
            raise

    try:
        config.load_incluster_config()  # Only useful for debugging purposes
        logger.debug("In-cluster config loaded successfully.")
    except Exception as e:
        logger.error("Failed to load in-cluster config: %s", e)
        raise

    # Without a config file, PyCalrissian uses the local cluster
    cluster_config_file = None
    # Use the internal backend service URL if the pipeline is run in the local cluster
    callback_url = f"http://{BACKEND_SERVICE_HOST}:{BACKEND_SERVICE_PORT}"

    if WORKSPACE_VCLUSTER_ENABLED:
        try:
            cluster_config_file = get_vcluster_config_file("ws-" + username)
            # Use the public URL if the pipeline is run in a vCluster
            callback_url = PUBLIC_URL
            # Saving the vCluster kubeconfig in a file allows debugging with e.g. k9s
            logger.debug("Workspace vCluster kubeconfig file: %s", cluster_config_file)
        except Exception as e:
            logger.error("Failed to obtain the Workspace vCluster config: %s", e)
            if WORKSPACE_VCLUSTER_REQUIRED:
                logger.error("Workspace vCluster is required. Aborting the execution")
                raise

    if SHARED_VCLUSTER_ENABLED:
        try:
            cluster_config_file = get_vcluster_config_file("application-quality-vcluster")
            callback_url = PUBLIC_URL
            logger.debug("Shared vCluster kubeconfig file: %s", cluster_config_file)
        except Exception as e:
            logger.error("Failed to obtain the Shared vCluster config: %s", e)
            if SHARED_VCLUSTER_REQUIRED:
                logger.error("Shared vCluster is required. Aborting the execution")
                raise

    # current_context = client.Configuration.get_default_copy()
    # print(f"Kubernetes API Server: {current_context.host}")
    # print(f"Using Authentication: {current_context.verify_ssl}")

    #
    # Create the kubernetes namespace on the cluster
    #
    namespace_name = f"applicationqualitypipeline-{run_id}"
    session = CalrissianContext(
        namespace=namespace_name,
        kubeconfig_file=cluster_config_file,
        storage_class=AQBB_STORAGECLASS,
        volume_size=AQBB_VOLUMESIZE,
        image_pull_secrets=AQBB_SECRET,
    )

    session.initialise()

    sonarqube_project = f"{username}-{pipeline_run.pipeline.pk}-{str(run_id)}"
    params = {
        "pipeline_id": str(pipeline_run.pipeline.pk),
        "run_id": str(run_id),
        "server_url": callback_url,
        # "sonarqube_project_key": sonarqube_project,
        # "sonarqube_project_name": sonarqube_project,
        # "sonarqube_server": SONARQUBE_SERVER,
        # "sonarqube_token": SONARQUBE_TOKEN,
    } | {
        f"{subworkflow}.{tool}.{input}": value
        for subworkflow, tools in parameters.items()
        for tool, inputs in tools.items()
        for input, value in inputs.items()
    }

    pipeline_run.inputs = params
    pipeline_run.save(update_fields=['inputs'])  # Overwrite previous value because of server_url
    logger.debug("Run %s updated with server url", pipeline_run.id)
    logger.debug("Pipeline parameters: %s", params)

    #
    # Create the Calrissian job
    #
    os.environ["CALRISSIAN_IMAGE"] = AQBB_CALRISSIANIMAGE  # This will maybe turn out superfluous

    job = CalrissianJob(
        cwl=cwl,
        params=params,
        runtime_context=session,
        pod_env_vars={
            "SONARQUBE_SERVER": SONARQUBE_SERVER,
            "SONARQUBE_TOKEN": SONARQUBE_TOKEN,
            "SONARQUBE_PROJECT_KEY": sonarqube_project,
            "SONARQUBE_PROJECT_NAME": sonarqube_project,
        },
        max_cores=AQBB_MAXCORES,
        max_ram=AQBB_MAXRAM,
        service_account=AQBB_SERVICEACCOUNT,
        tool_logs=True,
        debug=True,
    )

    # job.to_k8s_job()
    # job_cwl = job.to_dict()  # This can be useful data

    execution = CalrissianExecution(job=job, runtime_context=session)
    execution.submit()

    pipeline_run.status = "running"
    pipeline_run.save(update_fields=["status"])
    logger.debug("Run %s status updated: running", pipeline_run.id)

    #
    # Monitoring
    #
    execution.monitor(interval=20)
    try:
        usage = execution.get_usage_report()
    except UnboundLocalError:
        usage = "Couldn't copy usage report locally"
        logger.error(usage)

    try:
        output = execution.get_output()
    except JSONDecodeError:
        output = "Output file contains no JSON"
        logger.error(output)
    except UnboundLocalError:
        output = "Couldn't copy output locally"
        logger.error(output)

    logger.info("start time: %s", execution.get_start_time())
    logger.info("completion time: %s", execution.get_completion_time())
    logger.info("complete %s", execution.is_complete())
    logger.info("succeeded %s", execution.is_succeeded())
    # tool_logs = execution.get_tool_logs()  # Can be useful to avoid using save_tool

    #
    # Delete the Kubernetes namespace
    #
    if execution.is_succeeded():
        session.dispose()
    else:
        log = execution.get_log()
        logger.error("Execution failed for run %s", pipeline_run.id)
        logger.info(log)

    pipeline_run.refresh_from_db()
    pipeline_run.usage_report = usage
    # pipeline_run.start_time = execution.get_start_time()
    pipeline_run.completion_time = execution.get_completion_time()
    pipeline_run.status = execution.get_status().value
    pipeline_run.output = output

    pipeline_run.save()
    logger.info("Run %s completed", pipeline_run.id)
