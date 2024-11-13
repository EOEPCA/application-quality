from celery import shared_task
from backend.models import PipelineRun
from django.utils import timezone
from pycalrissian.run_workflow import run_workflow
import yaml


@shared_task
def run_workflow_task(pipeline_run_id: int, repo_url: str, repo_branch: str, slug: str, yaml_cwl: str):
    pipeline_run = PipelineRun.objects.get(id=pipeline_run_id)

    cwl = yaml.safe_load(yaml_cwl)

    workflow_output = run_workflow(
        repo_url=repo_url,
        repo_branch=repo_branch,
        slug=slug,
        run_id=str(pipeline_run.id),
        cwl=cwl,
    )

    pipeline_run.usage_report       = workflow_output.get("usage_report", "")
    pipeline_run.completion_time    = workflow_output.get("completion_time", timezone.now())
    pipeline_run.status             = workflow_output.get("status", "completed")
    pipeline_run.executed_cwl       = yaml_cwl
    pipeline_run.inputs             = workflow_output.get("inputs")
    pipeline_run.output             = workflow_output.get("output")
    # pipeline_run.jobs_run = workflow_output.get("jobs_run", 0)
    pipeline_run.save()
