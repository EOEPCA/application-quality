from celery import shared_task
from backend.utils.run_workflow import run_workflow


@shared_task
def run_workflow_task(
    run_id: int,
    repo_url: str,
    repo_branch: str,
    parameters: dict,
    pipeline_id: int,
    cwl: str,
    username: str,
):
    run_workflow(
        repo_url=repo_url,
        repo_branch=repo_branch,
        parameters=parameters,
        pipeline_id=pipeline_id,
        run_id=run_id,
        cwl=cwl,
        username=username,
    )
