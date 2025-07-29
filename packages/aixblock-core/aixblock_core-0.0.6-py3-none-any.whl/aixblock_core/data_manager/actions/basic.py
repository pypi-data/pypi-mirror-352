"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging

from datetime import datetime
from django.conf import settings
from core.permissions import AllPermissions
from core.redis import start_job_async_or_sync
from core.utils.common import load_func
from projects.models import Project

from tasks.models import (
    Annotation, Prediction, Task, bulk_update_stats_project_tasks
)
from webhooks.utils import emit_webhooks_for_instance
from webhooks.models import WebhookAction
from data_manager.functions import evaluate_predictions

all_permissions = AllPermissions()
logger = logging.getLogger(__name__)


def park_task(project, queryset, request, **kwargs):
    """ Park task by tasks ids

    :param project: project instance
    :param queryset: filtered tasks db queryset
    :param request: request instance
    """
    success_tasks = []
    failed_tasks = []
    parked_count = 0
    messages = []

    if project.max_parked_tasks and project.max_parked_tasks > 0:
        parked_count = Task.objects.filter(project=project).filter(assigned_to=request.user).count()

    for task in queryset:
        # Normal user
        if not request.user.is_superuser and not request.user.is_staff and not request.user.is_organization_admin:
            # Task parked already
            if task.assigned_to:
                if task.assigned_to == request.user:
                    success_tasks.append(task.id)
                    continue
                else:
                    failed_tasks.append(task.id)
                    messages.append(f"#{task.id}: Assigned to another user already")
                    continue
            else:
                if project.max_parked_tasks and 0 < project.max_parked_tasks <= parked_count:
                    failed_tasks.append(task.id)
                    messages.append(f"#{task.id}: Reached the limit of {project.max_parked_tasks} parked tasks")
                else:
                    task.assigned_to = request.user
                    task.save()
                    task.send_update_signal()
                    success_tasks.append(task.id)
                    parked_count += 1
        # Super user or staff
        else:
            if task.assigned_to != request.user:
                task.assigned_to = request.user
                task.save()
                task.send_update_signal()

            success_tasks.append(task.id)

    if len(failed_tasks) > 0:
        messages = ["Can not park tasks: #" + ", #".join(map(str, failed_tasks)),] + messages

    if len(success_tasks) > 0:
        messages = ["Parked tasks: #" + ", #".join(map(str, success_tasks)),] + messages

    return {
        'processed_items': queryset.count(),
        'detail': "\n".join(messages),
    }


def unpark_task(project, queryset, request, **kwargs):
    """ Unpark task by tasks ids

    :param project: project instance
    :param queryset: filtered tasks db queryset
    :param request: request instance
    """
    success_tasks = []
    failed_tasks = []
    messages = []

    for task in queryset:
        if not task.assigned_to:
            success_tasks.append(task.id)
            continue
        else:
            # Normal user
            if not request.user.is_superuser and not request.user.is_staff and not request.user.is_organization_admin:
                # Assignee is current user
                if task.assigned_to == request.user:
                    task.assigned_to = None
                    task.save()
                    task.send_update_signal()
                    success_tasks.append(task.id)
                    continue
                else:
                    failed_tasks.append(task.id)
                    continue
            # Super user or staff
            else:
                task.assigned_to = None
                task.save()
                task.send_update_signal()
                success_tasks.append(task.id)

    if len(failed_tasks) > 0:
        messages = ["Can not unpark tasks: #" + ", #".join(map(str, failed_tasks)),] + messages

    if len(success_tasks) > 0:
        messages = ['Unparked tasks: #' + ", #".join(map(str, success_tasks)),] + messages

    return {
        'processed_items': queryset.count(),
        'detail': "\n".join(messages),
    }


def retrieve_tasks_predictions(project, queryset, request, **kwargs):
    """ Retrieve predictions by tasks ids

    :param project: project instance
    :param queryset: filtered tasks db queryset
    """
    if not request.user.is_superuser and not request.user.is_staff and not request.user.is_organization_admin:
        return {'processed_items': 0, 'detail': 'You do not have permission to retrieve predictions.'}

    evaluate_predictions(queryset, request)
    return {'processed_items': queryset.count(), 'detail': 'Retrieved ' + str(queryset.count()) + ' predictions'}


def delete_tasks(project, queryset, request, **kwargs):
    """ Delete tasks by ids

    :param project: project instance
    :param queryset: filtered tasks db queryset
    """
    if not request.user.is_superuser and not request.user.is_staff and not request.user.is_organization_admin:
        return {'processed_items': 0, 'detail': 'You do not have permission to delete tasks.'}

    tasks_ids = list(queryset.values('id'))
    count = len(tasks_ids)
    tasks_ids_list = [task['id'] for task in tasks_ids]
    project_count = project.tasks.count()
    # unlink tasks from project
    queryset = Task.objects.filter(id__in=tasks_ids_list)
    queryset.update(project=None)
    # delete all project tasks
    if count == project_count:
        start_job_async_or_sync(Task.delete_tasks_without_signals_from_task_ids, tasks_ids_list)
        project.summary.reset()

    # delete only specific tasks
    else:
        # update project summary and delete tasks
        start_job_async_or_sync(async_project_summary_recalculation, tasks_ids_list, project.id)

    project.update_tasks_states(
        maximum_annotations_changed=False,
        overlap_cohort_percentage_changed=False,
        tasks_number_changed=True
    )

    if project.is_audio_project():
        project.update_audio_project_stats()

    # emit webhooks for project
    emit_webhooks_for_instance(project.organization, project, WebhookAction.TASKS_DELETED, tasks_ids)

    # remove all tabs if there are no tasks in project
    # reload = False
    # if not project.tasks.exists():
    #     project.views.all().delete()
    #     reload = True

    return {'processed_items': count, 'reload': True,
            'detail': 'Deleted ' + str(count) + ' tasks'}


def delete_tasks_annotations(project, queryset, request, **kwargs):
    """ Delete all annotations by tasks ids

    :param project: project instance
    :param queryset: filtered tasks db queryset
    """
    if not request.user.is_superuser and not request.user.is_staff and not request.user.is_organization_admin:
        return {'processed_items': 0, 'detail': 'You do not have permission to bulk delete annotations.'}

    task_ids = queryset.values_list('id', flat=True)
    annotations = Annotation.objects.filter(task__id__in=task_ids)
    count = annotations.count()

    # take only tasks where annotations were deleted
    real_task_ids = set(list(annotations.values_list('task__id', flat=True)))
    annotations_ids = list(annotations.values('id'))
    # remove deleted annotations from project.summary
    project.summary.remove_created_annotations_and_labels(annotations)
    annotations.delete()
    emit_webhooks_for_instance(project.organization, project, WebhookAction.ANNOTATIONS_DELETED, annotations_ids)
    start_job_async_or_sync(bulk_update_stats_project_tasks, queryset.filter(is_labeled=True))
    start_job_async_or_sync(project.update_tasks_counters, task_ids)

    tasks = Task.objects.filter(id__in=real_task_ids)
    tasks.update(updated_at=datetime.now(), updated_by=request.user)

    # LSE postprocess
    postprocess = load_func(settings.DELETE_TASKS_ANNOTATIONS_POSTPROCESS)
    if postprocess is not None:
        tasks = Task.objects.filter(id__in=task_ids)
        postprocess(project, tasks, **kwargs)

    return {'processed_items': count,
            'detail': 'Deleted ' + str(count) + ' annotations'}


def delete_tasks_predictions(project, queryset, request, **kwargs):
    """ Delete all predictions by tasks ids

    :param project: project instance
    :param queryset: filtered tasks db queryset
    """
    if not request.user.is_superuser and not request.user.is_staff and not request.user.is_organization_admin:
        return {'processed_items': 0, 'detail': 'You do not have permission to bulk delete predictions.'}

    task_ids = queryset.values_list('id', flat=True)
    predictions = Prediction.objects.filter(task__id__in=task_ids)
    count = predictions.count()
    predictions.delete()
    start_job_async_or_sync(project.update_tasks_counters, task_ids)
    return {'processed_items': count, 'detail': 'Deleted ' + str(count) + ' predictions'}


def async_project_summary_recalculation(tasks_ids_list, project_id):
    queryset = Task.objects.filter(id__in=tasks_ids_list)
    project = Project.objects.get(id=project_id)
    project.summary.remove_created_annotations_and_labels(Annotation.objects.filter(task__in=queryset))
    project.summary.remove_data_columns(queryset)
    Task.delete_tasks_without_signals(queryset)


actions = [
    # {
    #     'entry_point': park_task,
    #     'permission': all_permissions.annotations_create,
    #     'title': 'Park task',
    #     'order': 80,
    # },
    {
        'entry_point': unpark_task,
        'permission': all_permissions.annotations_create,
        'title': 'Unpark task',
        'order': 81,
    },
    {
        'entry_point': retrieve_tasks_predictions,
        'permission': all_permissions.predictions_any,
        'title': 'Auto Predict Annotations',
        'order': 90,
        # 'dialog': {
        #     'text': 'Send the selected tasks to all ML backends connected to the project.'
        #             'This operation might be abruptly interrupted due to a timeout. '
        #             'The recommended way to get predictions is to update tasks using the [AiXBlock API](/docs/api).'
        #             'Please confirm your action.',
        #     'type': 'confirm'
        # }
    },
    {
        'entry_point': delete_tasks,
        'permission': all_permissions.tasks_delete,
        'title': 'Delete Tasks',
        'order': 100,
        'reload': True,
        'dialog': {
            'text': 'You are going to delete the selected tasks. Please confirm your action.',
            'type': 'confirm'
        }
    },
    {
        'entry_point': delete_tasks_annotations,
        'permission': all_permissions.tasks_delete,
        'title': 'Delete Annotations',
        'order': 101,
        'dialog': {
            'text': 'You are going to delete all annotations from the selected tasks. Please confirm your action.',
            'type': 'confirm'
        }
    },
    {
        'entry_point': delete_tasks_predictions,
        'permission': all_permissions.predictions_any,
        'title': 'Delete Predictions',
        'order': 102,
        'dialog': {
            'text': 'You are going to delete all predictions from the selected tasks. Please confirm your action.',
            'type': 'confirm'
        }
    }
]
