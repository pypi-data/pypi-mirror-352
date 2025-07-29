from django_dbq.models import Job
from tasks.optimize_task import optimize_task


def processor(job: Job):
    try:
        optimize_task(
            task_id=job.workspace["task_pk"],
            storage_scheme=job.workspace["storage_scheme"],
            storage_pk=job.workspace["storage_pk"],
        )
    except Exception as e:
        print(f"Failed to run optimize task job: {e}")
