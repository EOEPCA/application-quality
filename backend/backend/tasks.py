from celery import shared_task
from backend.utils.run_workflow import run_workflow


@shared_task
def run_workflow_task(run_id: int, repo_url: str, repo_branch: str, slug: str, cwl: str):
    run_workflow(
        repo_url=repo_url,
        repo_branch=repo_branch,
        slug=slug,
        run_id=run_id,
        cwl=cwl,
    )
