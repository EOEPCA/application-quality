import base64
import logging
import os

from datetime import datetime
from json.decoder import JSONDecodeError
from kubernetes import config

from backend.models import PipelineRun
from backend.utils.github import (
    GH_CONTEXT_STATUS,
    post_quality_state as gh_post_quality_state,
    get_properties as gh_get_properties,
)
from backend.utils.tools import getenv_bool
from backend.utils.workspaces import get_vcluster_config_file
from pycalrissian.context import CalrissianContext
from pycalrissian.execution import CalrissianExecution
from pycalrissian.job import CalrissianJob
from rule_engine import Rule


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
# Backend service, possibly replicated in a virtual cluster (for storing reports)
BACKEND_SERVICE_HOST = os.getenv(
    "BACKEND_SERVICE_HOST",
    "application-quality-api.application-quality.svc.cluster.local"
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


def _get_cluster_config_file(callback_url: str, username: str = "") -> str:
    cluster_config_file = None

    if WORKSPACE_VCLUSTER_ENABLED:
        try:
            cluster_config_file = get_vcluster_config_file("ws-" + username)
            # Use the public URL if the pipeline is run in a vCluster
            callback_url = PUBLIC_URL
            # Saving the vCluster kubeconfig in a file allows debugging with e.g. k9s
            logger.debug("Workspace vCluster kubeconfig file: %s", cluster_config_file)
        except Exception as e:
            logger.error("Failed to obtain the Workspace vCluster config: %s", e)
            cluster_config_file = None
            if WORKSPACE_VCLUSTER_REQUIRED:
                logger.error("Workspace vCluster is required. Aborting the execution")
                raise

    if cluster_config_file is None and SHARED_VCLUSTER_ENABLED:
        try:
            cluster_config_file = get_vcluster_config_file("application-quality-vcluster")
            callback_url = PUBLIC_URL
            logger.debug("Shared vCluster kubeconfig file: %s", cluster_config_file)
        except Exception as e:
            logger.error("Failed to obtain the Shared vCluster config: %s", e)
            cluster_config_file = None
            if SHARED_VCLUSTER_REQUIRED:
                logger.error("Shared vCluster is required. Aborting the execution")
                raise

    return callback_url, cluster_config_file


def _create_image_pull_secrets(registry: str, username: str, password: str) -> dict:
    """
    Make a string with the username and the password,
    turn it into a string literal (encode()),
    encode the literal in base 64,
    turn the encoded string literal back into a regular string (decode()).
    """
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {
        "auths": {
            "registry.gitlab.com": {"auth": ""},
            "https://index.docker.io/v1/": {"auth": ""},
            registry: {"auth": auth},
        }
    }


def _check_digest_rules(pipeline_run: PipelineRun, pr_digest: dict) -> str:
    """
    Example rule:
        "(error == 0 and critical == 0) or security < 1"
    """
    logger.info("Check quality rules to pipeline run %s", pipeline_run.id)
    quality_rules = pr_digest.get("quality_rules", {})
    logger.info("Quality rules: %s", quality_rules)
    digest_issues = pr_digest.get("issues", {})
    result = None
    try:
        # Check the "pass_with_comments" rule, if present
        if "pass_with_comments" in quality_rules:
            rule = Rule(quality_rules["pass_with_comments"])
            logger.debug("Checking pass_with_comments rule: %s", rule)
            if rule.matches(digest_issues):
                result = "pass_with_comments"
        if result is None:
            if "pass" in quality_rules:
                rule = Rule(quality_rules["pass"])
                logger.debug("Checking pass rule: %s", rule)
                if rule.matches(digest_issues):
                    result = "pass"
                else:
                    result = "fail"
            else:
                # No "pass" rule => Cannot determine the quality
                logger.debug("'pass' rule required to deduce the quality.")
                result = "unknown"
    except Exception as e:
        logger.error("Failed to check quality rules: %s", e)
        result = "exception"
    return result


def _generate_pipeline_run_digest(pipeline_run: PipelineRun) -> dict:
    logger.debug("Generate digest for pipeline run %s", pipeline_run.id)
    pr_digest = {
        "properties": {
            "name": "",
            "version": "",
        },
        "issues": {
            "info": 0,
            "convention": 0,
            "warning": 0,
            "error": 0,
            "security": 0,
            "critical": 0,
        },
        "quality_rules": None,
        "digest_quality": None,
        "created_at": datetime.now().isoformat(),
    }
    # Collect the issue counts from the job reports digest
    for job_report in pipeline_run.jobreports.all():
        if job_report.digest:
            issues = job_report.digest.get("issues", {})
            for key in ["info", "convention", "warning", "error", "security", "critical"]:
                pr_digest["issues"][key] += issues.get(key, 0)
    # Retrieve the application quality rules from the pipeline definition
    # "pass": "applications with good quality pass that rule",
    # "pass_with_comments": "applications with minor warnings/comments pass that rule",
    # Otherwise, the quality is "fail"
    try:
        quality_rules = pipeline_run.pipeline.quality_rules
    except Exception as e:
        logger.error("Error while retrieving pipeline quality rules: %s", e)
        quality_rules = {
            "pass": "error == 0 and critical == 0 and security == 0 and warning == 0"
        }
    pr_digest["quality_rules"] = quality_rules
    pr_digest["digest_quality"] = _check_digest_rules(pipeline_run, pr_digest)
    return pr_digest


def _update_pipeline_run(pipeline_run: PipelineRun, execution: CalrissianExecution):
    logger.debug("Update pipeline run %s", pipeline_run.id)
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

    digest = _generate_pipeline_run_digest(pipeline_run)
    pipeline_run.refresh_from_db()
    pipeline_run.usage_report = usage
    # pipeline_run.start_time = execution.get_start_time()
    pipeline_run.completion_time = execution.get_completion_time()
    pipeline_run.status = execution.get_status().value
    pipeline_run.output = output
    pipeline_run.digest = digest

    pipeline_run.save()
    logger.info("Pipeline run %s updated", pipeline_run.id)

    if digest.get("digest_quality", None) in ["pass", "pass_with_comments"]:
        update_quality_status(pipeline_run, GH_CONTEXT_STATUS.SUCCESS)
    else:
        update_quality_status(pipeline_run, GH_CONTEXT_STATUS.FAILURE)


def update_quality_status(pipeline_run: PipelineRun, status: str):
    """
    This function updates in GitHub or GitLab the quality status of the code being analysed.
    The pipeline run must be linked to a push event issued by GitHub or GitLab.
    The parameters (owner, repository, commit SHA) are extracted from the event body.
    Before starting the workflow, the status is set to PENDING.
    When the execution is complete, the status depends on the computed digest: SUCCESS or FAILURE.
    """
    logger.debug("Update application quality status for Run %s", pipeline_run.id)
    response = None
    try:
        # Obtain the trigger event, if any
        event = pipeline_run.triggered_by.first()
        if not event:
            # This pipeline run has not been triggered by an event
            logger.info(
                "Run %s not triggered by an event. Skipping quality status update.",
                pipeline_run.id,
            )
            return
        # Extract the owner, repository, and commit SHA from the event body
        # and update the quality status in GitHub
        if event.event_type.startswith("org.eoepca.webhook.github"):
            owner, repo, sha = gh_get_properties(event.event_body)
            response = gh_post_quality_state(owner, repo, sha, status)
            logger.debug(
                "Application quality status updated in GitHub for Run %s",
                pipeline_run.id,
            )
        elif event.event_type.startswith("org.eoepca.webhook.gitlab"):
            # Updating quality status in GitLab is not supported yet
            logger.warning("Application quality status in GitLab is not supported yet.")
        else:
            logger.info(
                "Run %s not triggered by a push or pull_request event: %s. Skipping quality status update.",
                pipeline_run.id,
                event.event_type,
            )
    except Exception as e:
        logger.error(
            "Failed to update application quality status for Run %s: %s",
            pipeline_run.id,
            e,
        )
        raise e
    return response


def run_workflow(
    parameters: dict,
    run_id: int,
    cwl: dict,
    username: str,
) -> dict:
    pipeline_run = PipelineRun.objects.get(id=run_id)
    update_quality_status(pipeline_run, GH_CONTEXT_STATUS.PENDING)

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

    # Use the internal backend service URL if the pipeline is run in the local cluster
    callback_url = f"http://{BACKEND_SERVICE_HOST}:{BACKEND_SERVICE_PORT}"

    # Without a config file, PyCalrissian uses the local cluster
    callback_url, cluster_config_file = _get_cluster_config_file(callback_url)

    # If cluster_config_file is None here, the ultimate option (if vclusters are not required)
    # is running the pipeline in the host cluster

    # TODO: Remove Sonarqube parameters
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

    namespace_name = f"applicationqualitypipeline-{run_id}"
    session = CalrissianContext(
        namespace=namespace_name,
        kubeconfig_file=cluster_config_file,
        storage_class=AQBB_STORAGECLASS,
        volume_size=AQBB_VOLUMESIZE,
        image_pull_secrets=AQBB_SECRET,
    )

    session.initialise()

    # Create the Calrissian job
    # https://terradue.github.io/pycalrissian/gettingstarted/#create-the-calrissianjob
    os.environ["CALRISSIAN_IMAGE"] = AQBB_CALRISSIANIMAGE

    job = CalrissianJob(
        cwl=cwl,
        params=params,
        runtime_context=session,
        # TODO: Remove Sonarqube parameters
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

    # Monitoring
    execution.monitor(interval=20)

    # Update the pipeline run with outputs, resource consumption, digests, quality, etc.
    _update_pipeline_run(pipeline_run, execution)

    # Delete the Kubernetes namespace
    if execution.is_succeeded():
        session.dispose()
    else:
        log = execution.get_log()
        logger.error("Execution failed for run %s", pipeline_run.id)
        logger.info(log)
    
    logger.info("Run %s completed", pipeline_run.id)
