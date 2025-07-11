from celery import shared_task
from backend.utils.run_workflow import run_workflow


@shared_task
def run_workflow_task(
    run_id: int,
    parameters: dict,
    cwl: str,
    username: str,
):
    run_workflow(
        parameters=parameters,
        run_id=run_id,
        cwl=cwl,
        username=username,
    )
