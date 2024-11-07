# from kubernetes.client.models.v1_job import V1Job
from kubernetes import config, client
from pycalrissian.context import CalrissianContext
from pycalrissian.execution import CalrissianExecution
from pycalrissian.job import CalrissianJob

import logging
import os
# import base64

AQBB_STORAGECLASS = os.getenv("AQBB_STORAGECLASS", "standard")
AQBB_VOLUMESIZE = os.getenv("AQBB_VOLUMESIZE", "5Gi")
AQBB_CALRISSIANIMAGE = os.getenv("AQBB_CALRISSIANIMAGE", "terradue/calrissian:0.14.0")
AQBB_MAXCORES = os.getenv("AQBB_MAXCORES", "2")
AQBB_MAXRAM = os.getenv("AQBB_MAXRAM", "2Gi")
AQBB_SECRET = os.getenv("AQBB_SECRET", None)
AQBB_SERVICEACCOUNT = os.getenv("AQBB_SERVICEACCOUNT", None)
BACKEND_SERVICE_HOST = os.getenv("BACKEND_SERVICE_HOST", "django-service.aqbb.svc.cluster.local")
BACKEND_SERVICE_PORT = os.getenv("BACKEND_SERVICE_PORT", "80")


def run_workflow(repo_url: str, slug: str, run_id: str, cwl: dict) -> dict:
    None
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

    """
	Create the kubernetes namespace on the cluster
	"""

    try:
        config.load_incluster_config()  # Not necessary anymore, normally
        logging.info("In-cluster config loaded successfully.")
        print("In-cluster config loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load in-cluster config: {e}")
        print("Config failed.")
        raise

    current_context = client.Configuration.get_default_copy()
    print(f"Kubernetes API Server: {current_context.host}")
    print(f"Using Authentication: {current_context.verify_ssl}")

    namespace_name = f"applicationqualitypipeline-{run_id}"
    session = CalrissianContext(
        namespace=namespace_name,
        storage_class=AQBB_STORAGECLASS,
        volume_size=AQBB_VOLUMESIZE,
        image_pull_secrets=AQBB_SECRET,
    )

    session.initialise()

    params = {
        "repo_url": repo_url,
        "run_id": run_id,
        "pipeline_id": slug,
        "server_url": f"{BACKEND_SERVICE_HOST}:{BACKEND_SERVICE_PORT}",
    }

    """
	Create the Calrissian job
	"""
    os.environ["CALRISSIAN_IMAGE"] = (
        AQBB_CALRISSIANIMAGE  # This will maybe turn out superfluous
    )
    job = CalrissianJob(
        cwl=cwl,
        params=params,
        runtime_context=session,
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

    """
	Monitoring
	"""
    execution.monitor(interval=20)
    log = execution.get_log()
    logging.info(log)
    usage = execution.get_usage_report()
    usage
    from json.decoder import JSONDecodeError  # Can't stay here

    try:
        output = execution.get_output()
    except JSONDecodeError:
        output = "Output file empty"
        print(output)
    logging.info(execution.get_start_time())
    logging.info(execution.get_completion_time())
    logging.info(f"complete {execution.is_complete()}")
    logging.info(f"succeeded {execution.is_succeeded()}")
    execution.get_tool_logs()

    """
	Delete the Kubernetes namespace (and everything that's associated to it)
	"""
    if execution.is_succeeded():
        session.dispose()

    workflow_report = {
        "usage_report": usage,
        "start_time": execution.get_start_time(),
        "completion_time": execution.get_completion_time(),
        "status": execution.get_status().value,
        "output": output,
    }

    # print(workflow_report)

    return workflow_report
