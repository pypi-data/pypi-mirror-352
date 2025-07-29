import logging

from django_dbq.models import Job
from io_storages.functions import get_all_project_storage
from projects.models import Project
from tasks.models import Task, Annotation
from users.models import User


def processor(job):
    try:
        project = Project.objects.filter(pk=job.workspace["project_id"]).first()
        user = User.objects.filter(pk=job.workspace["user_id"]).first()
        tasks = job.workspace["tasks"]
        new_tasks = []
        new_annotations = []
        data_need_to_be_optimized = project.data_need_to_be_optimized()
        storage = get_all_project_storage(project.pk)[0]

        for task in tasks:
            new_task = Task(
                data=task["data"],
                project=project,
                created_by=user,
                total_annotations=1,
                is_data_optimized=not data_need_to_be_optimized
            )

            new_tasks.append(new_task)

            new_annotations.append(
                Annotation(
                    result=task["result"],
                    task=new_task,
                    completed_by=user,
                )
            )

            if data_need_to_be_optimized:
                Job.objects.create(name="optimize_task", workspace={
                    "task_pk": new_task.pk,
                    "storage_scheme": storage.url_scheme,
                    "storage_pk": storage.pk,
                })

        if len(new_tasks) > 0:
            Task.objects.bulk_create(new_tasks)
            Annotation.objects.bulk_create(new_annotations)
            logging.info(f"Created {len(new_tasks)} task(s)")
    except Exception as e:
        print(f"Failed to run create tasks job: {e}")
