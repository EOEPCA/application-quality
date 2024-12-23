import json
import logging
import os

from backend.models import JobReport, PipelineRun
from backend.serializers import PipelineRunSerializer, JobReportSerializer
from opensearchpy import OpenSearch
from urllib.parse import urlparse


OPENSEARCH_ENABLED_STR = os.getenv("OPENSEARCH_ENABLED", "false")
OPENSEARCH_ENABLED = str(OPENSEARCH_ENABLED_STR).lower() == "true"
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", None)
OPENSEARCH_INDEX_RUNS = os.getenv("OPENSEARCH_INDEX_RUNS", "application-quality-pipeline-runs")
OPENSEARCH_INDEX_REPORTS = os.getenv("OPENSEARCH_INDEX_REPORTS", "application-quality-pipeline-run-reports")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", None)
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", None)
OPENSEARCH_LOG_LEVEL = os.getenv("OPENSEARCH_LOG_LEVEL", "INFO")

OPENSEARCH_CLIENT = None

logger = logging.getLogger(__name__)
logger.setLevel(OPENSEARCH_LOG_LEVEL)


if OPENSEARCH_ENABLED:
    try:
        parsed_url = urlparse(OPENSEARCH_URL)
        OPENSEARCH_CLIENT = OpenSearch(
            hosts=[{"host": parsed_url.hostname, "port": parsed_url.port}],
            http_compress=True,
            http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        logger.info("Indexing in OpenSearch is ENABLED")
    except Exception as e:
        logger.warning("Failed to initialise the OpenSearch client", exc_info=True)
else:
    logger.info("Indexing in OpenSearch is DISABLED")


def index_pipeline_run(pipeline_run: PipelineRun):
    if OPENSEARCH_CLIENT is None:
        return
    try:
        pipeline_run_json = PipelineRunSerializer(pipeline_run).data
        if pipeline_run_json.get("usage_report", "") == "":
            pipeline_run_json["usage_report"] = {}
        logger.info(f'Indexing pipeline run {pipeline_run_json["id"]} in OpenSearch')
        OPENSEARCH_CLIENT.index(
            index=OPENSEARCH_INDEX_RUNS,
            body=pipeline_run_json,
            id=pipeline_run_json["id"],
            refresh=True,
        )
    except Exception as e:
        logger.error("Failed to index the pipeline run in OpenSearch", exc_info=True)


def index_pipeline_job_report(pipeline_job_report: JobReport):
    if OPENSEARCH_CLIENT is None:
        return
    try:
        job_report_json = JobReportSerializer(pipeline_job_report).data
        job_report_id = f'{job_report_json["run"]}_{job_report_json["name"]}'
        logger.info(f"Indexing pipeline job report {job_report_id} in OpenSearch")
        OPENSEARCH_CLIENT.index(
            index=OPENSEARCH_INDEX_REPORTS,
            body=job_report_json,
            id=job_report_id,
            refresh=True,
        )
    except Exception as e:
        logger.error("Failed to index the pipeline job report in OpenSearch", exc_info=True)
