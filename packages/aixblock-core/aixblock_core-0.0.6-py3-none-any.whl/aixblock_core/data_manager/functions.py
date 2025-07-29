"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import time

import requests
import ujson as json

from collections import OrderedDict

from core.audit_logs import send_audit_log
from django.db import transaction
from django.db.models import Q, Count
from django.conf import settings
from rest_framework.generics import get_object_or_404

from core.utils.common import int_from_request
from data_manager.prepare_params import PrepareParams
from data_manager.models import View
from tasks.models import Task
from urllib.parse import unquote
from core.feature_flags import flag_set

TASKS = 'tasks:'
logger = logging.getLogger(__name__)


class DataManagerException(Exception):
    pass


def get_all_columns(project, *_):
    """ Make columns info for the frontend data manager
    """
    result = {'columns': []}
    organize_users_items = []

    for user in project.organization.users.all():
        organize_users_items.append({
            "title": user.email,
            "value": user.id,
        })

    result['columns'] += [
        # --- Tasks ---
        {
            'id': 'id',
            'title': "ID",
            'type': 'Number',
            'help': 'Task ID',
            'target': 'tasks',
            'visibility_defaults': {
                'explore': True,
                'labeling': False
            }
        }
    ]

    if flag_set('ff_back_2070_inner_id_12052022_short', user=project.organization.created_by):
        result['columns'] += [{
            'id': 'inner_id',
            'title': "Inner ID",
            'type': 'Number',
            'help': 'Internal task ID starting from 1 for the current project',
            'target': 'tasks',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        }]

    result['columns'] += [
        {
            'id': 'completed_at',
            'title': 'Completed',
            'type': 'Datetime',
            'target': 'tasks',
            'help': 'Last annotation date',
            'visibility_defaults': {
                'explore': True,
                'labeling': False
            }
        },
        {
            'id': 'total_annotations',
            'title': 'Annotations',
            'type': "Number",
            'target': 'tasks',
            'help': 'Total annotations per task',
            'visibility_defaults': {
                'explore': True,
                'labeling': True
            }
        },
        {
            'id': 'cancelled_annotations',
            'title': "Cancelled",
            'type': "Number",
            'target': 'tasks',
            'help': 'Total cancelled (skipped) annotations',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'total_predictions',
            'title': "Predictions",
            'type': "Number",
            'target': 'tasks',
            'help': 'Total predictions per task',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'annotators',
            'title': 'Annotated by',
            'type': 'List',
            'target': 'tasks',
            'help': 'All users who completed the task',
            'schema': {'items': organize_users_items},
            'visibility_defaults': {
                'explore': True,
                'labeling': False
            }
        },
        {
            'id': 'annotations_results',
            'title': "Annotation results",
            'type': "String",
            'target': 'tasks',
            'help': 'Annotation results stacked over all annotations',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'annotations_ids',
            'title': "Annotation IDs",
            'type': "String",
            'target': 'tasks',
            'help': 'Annotation IDs stacked over all annotations',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'predictions_score',
            'title': "Prediction score",
            'type': "Number",
            'target': 'tasks',
            'help': 'Average prediction score over all task predictions',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'predictions_model_versions',
            'title': "Prediction model versions",
            'type': 'List',
            'target': 'tasks',
            'help': 'Model versions aggregated over all predictions',
            'schema': {'items': project.get_model_versions()},
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'predictions_results',
            'title': "Prediction results",
            'type': "String",
            'target': 'tasks',
            'help': 'Prediction results stacked over all predictions',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        # {
        #     'id': 'file_upload',
        #     'title': "Upload filename",
        #     'type': "String",
        #     'target': 'tasks',
        #     'help': 'Filename of uploaded file',
        #     'visibility_defaults': {
        #         'explore': False,
        #         'labeling': False
        #     }
        # },
        # {
        #     'id': 'storage_filename',
        #     'title': "Storage filename",
        #     'type': "String",
        #     'target': 'tasks',
        #     'help': 'Filename from import storage',
        #     'visibility_defaults': {
        #         'explore': False,
        #         'labeling': False
        #     }
        # },
        {
            'id': 'created_at',
            'title': 'Created at',
            'type': 'Datetime',
            'target': 'tasks',
            'help': 'Task creation time',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'created_by',
            'title': 'Created by',
            'type': 'List',
            'target': 'tasks',
            'help': 'User who created the task',
            'schema': {'items': organize_users_items},
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'updated_at',
            'title': 'Updated at',
            'type': 'Datetime',
            'target': 'tasks',
            'help': 'Task update time',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'updated_by',
            'title': 'Updated by',
            'type': 'List',
            'target': 'tasks',
            'help': 'User who did the last task update',
            'schema': {'items': organize_users_items},
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        {
            'id': 'avg_lead_time',
            'title': "Lead Time",
            'type': 'Number',
            'help': 'Average lead time over all annotations (seconds)',
            'target': 'tasks',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
        # {
        #     'id': 'locked_by',
        #     'title': 'Locked by',
        #     'type': 'List',
        #     'target': 'tasks',
        #     'help': 'User who is locking the task',
        #     'schema': {'items': organize_users_items},
        #     'visibility_defaults': {
        #         'explore': False,
        #         'labeling': False
        #     }
        # },
        {
            'id': 'assigned_to',
            'title': 'Assignee',
            'type': 'List',
            'target': 'tasks',
            'help': 'User who assigned to the task',
            'schema': {'items': organize_users_items},
            'visibility_defaults': {
                'explore': True,
                'labeling': False
            }
        },
        {
            'id': 'is_data_optimized',
            'title': "Optimized Data",
            'type': 'Boolean',
            'help': 'Indicate that the data has been optimized',
            'target': 'tasks',
            'visibility_defaults': {
                'explore': False,
                'labeling': False
            }
        },
    ]

    if project.need_to_qa:
        result['columns'] += [
            {
                'id': 'reviewed_by',
                'title': 'QA by',
                'type': 'List',
                'target': 'tasks',
                'help': 'User who did the last task review',
                'schema': {'items': organize_users_items},
                'visibility_defaults': {
                    'explore': True,
                    'labeling': False
                }
            },
            {
                'id': 'reviewed_result',
                'title': "QA result",
                'type': "List",
                'target': 'tasks',
                'help': 'The last task reviewed result',
                'schema': {
                    'items': [
                        {'title': 'APPROVED', 'value': 'approved'},
                        {'title': 'REJECTED', 'value': 'rejected'},
                    ],
                },
                'visibility_defaults': {
                    'explore': True,
                    'labeling': False
                }
            },
            {
                'id': 'is_in_review',
                'title': "In QA pool",
                'type': 'Boolean',
                'help': 'Task QA phase',
                'target': 'tasks',
                'visibility_defaults': {
                    'explore': True,
                    'labeling': False
                }
            },
        ]

    if project.need_to_qc:
        result['columns'] += [
            {
                'id': 'qualified_by',
                'title': 'QC by',
                'type': 'List',
                'target': 'tasks',
                'help': 'User who did the last task qualify',
                'schema': {'items': organize_users_items},
                'visibility_defaults': {
                    'explore': False,
                    'labeling': False
                }
            },
            {
                'id': 'qualified_result',
                'title': "QC result",
                'type': "List",
                'target': 'tasks',
                'help': 'The last task qualified result',
                'schema': {
                    'items': [
                        {'title': 'QUALIFIED', 'value': 'qualified'},
                        {'title': 'UNQUALIFIED', 'value': 'unqualified'},
                    ],
                },
                'visibility_defaults': {
                    'explore': True,
                    'labeling': False
                }
            },
            {
                'id': 'is_in_qc',
                'title': "In QC pool",
                'type': 'Boolean',
                'help': 'Task qualifying phase',
                'target': 'tasks',
                'visibility_defaults': {
                    'explore': True,
                    'labeling': False
                }
            },
        ]

    # frontend uses MST data model, so we need two directional referencing parent <-> child
    task_data_children = []
    i = 0

    data_types = OrderedDict()

    # add data types from config again
    project_data_types = {}
    for key, value in project.data_types.items():
        # skip keys from Repeater tag, because we already have its base data,
        # e.g.: skip 'image[{{idx}}]' because we have 'image' list already
        if '[' not in key:
            project_data_types[key] = value
    data_types.update(project_data_types.items())

    # all data types from import data
    all_data_columns = project.summary.all_data_columns
    if all_data_columns:
        data_types.update({key: 'Unknown' for key in all_data_columns if key not in data_types})

    if 'duration' in data_types:
        data_types.update({'duration': 'Duration'})

    if 'channels' in data_types:
        data_types.update({'channels': 'Number'})

    if 'bit_rate' in data_types:
        data_types.update({'bit_rate': 'Number'})

    if 'sample_rate' in data_types:
        data_types.update({'sample_rate': 'Number'})

    if 'pcd' in data_types:
        del data_types['pcd']

    # remove $undefined$ if there is one type at least in labeling config, because it will be resolved automatically
    if len(project_data_types) > 0:
        data_types.pop(settings.DATA_UNDEFINED_NAME, None)

    for key, data_type in list(data_types.items()):  # make data types from labeling config first
        column = {
            'id': key,
            'title': key if key != settings.DATA_UNDEFINED_NAME else 'data',
            'type': data_type if data_type in ['Image', 'Audio', 'AudioPlus', 'Video', 'Duration', 'Unknown',
                                               'Number'] else 'String',
            'target': 'tasks',
            'parent': 'data',
            'visibility_defaults': {
                'explore': True,
                'labeling': key in project_data_types or key == settings.DATA_UNDEFINED_NAME
            }
        }
        result['columns'].append(column)
        task_data_children.append(column['id'])
        i += 1

    # --- Data root ---
    data_root = {
        'id': 'data',
        'title': "data",
        'type': "List",
        'target': 'tasks',
        'children': task_data_children
    }

    result['columns'].append(data_root)

    return result


def get_prepare_params(request, project):
    """ This function extract prepare_params from
        * view_id if it's inside of request data
        * selectedItems, filters, ordering if they are in request and there is no view id
    """
    # use filters and selected items from view
    view_id = int_from_request(request.GET, 'view', 0) or int_from_request(request.data, 'view', 0)
    if view_id > 0:
        view = get_object_or_404(View, pk=view_id)
        if view.project.pk != project.pk:
            raise DataManagerException('Project and View mismatch')
        prepare_params = view.get_prepare_tasks_params(add_selected_items=True)
        prepare_params.request = request

    # use filters and selected items from request if it's specified
    else:
        # query arguments from url
        if 'query' in request.GET:
            data = json.loads(unquote(request.GET['query']))
        # data payload from body
        else:
            data = request.data

        selected = data.get('selectedItems', {"all": True, "excluded": []})
        if not isinstance(selected, dict):
            raise DataManagerException('selectedItems must be dict: {"all": [true|false], '
                                       '"excluded | included": [...task_ids...]}')
        filters = data.get('filters', None)
        ordering = data.get('ordering', [])
        prepare_params = PrepareParams(project=project.id, selectedItems=selected, data=data,
                                       filters=filters, ordering=ordering, request=request)
    return prepare_params


def get_prepared_queryset(request, project):
    prepare_params = get_prepare_params(request, project)
    queryset = Task.prepared.only_filtered(prepare_params=prepare_params)
    return queryset


def evaluate_predictions(tasks, request=None):
    """ Call ML backend for prediction evaluation of the task queryset
    """
    if not tasks:
        return

    project = tasks[0].project

    for ml_backend in project.ml_backends.filter(deleted_at__isnull=True).all():
        # tasks = tasks.filter(~Q(predictions__model_version=ml_backend.model_version))
        ml_backend.predict_tasks(tasks, request)


def filters_ordering_selected_items_exist(data):
    return data.get('filters') or data.get('ordering') or data.get('selectedItems')


def custom_filter_expressions(*args, **kwargs):
    pass


def preprocess_filter(_filter, *_):
    return _filter


def preprocess_field_name(raw_field_name, only_undefined_field=False):
    field_name = raw_field_name.replace("filter:", "")
    field_name = field_name.replace("tasks:", "")
    ascending = False if field_name[0] == '-' else True  # detect direction
    field_name = field_name[1:] if field_name[0] == '-' else field_name  # remove direction
    if field_name.startswith("data."):
        if only_undefined_field:
            field_name = f'data__{settings.DATA_UNDEFINED_NAME}'
        else:
            field_name = field_name.replace("data.", "data__")
    return field_name, ascending


def new_task(user, project):
    is_qa = None
    is_qc = None
    try:
        from organizations.models import Organization_Project_Permission
        user_role = Organization_Project_Permission.objects.filter(user_id=user.id, project_id=project.id, deleted_at__isnull=True).order_by("-id").first()
        is_qa = user_role.is_qa
        is_qc = user_role.is_qc
    except Exception as e:
        print(e)

    is_admin = user.is_superuser or user.is_organization_admin
    task = None

    with transaction.atomic():
        parked_tasks = Task.objects.filter(project_id=project.id).filter(assigned_to=user).all()
        count = 0
        user_qa = user.is_qa if is_qa==None else is_qa
        user_qc = user.is_qc if is_qc==None else is_qc

        for task in parked_tasks:
            if project.max_parked_tasks > len(parked_tasks) - count:
                break

            count += 1
            task.assigned_to = None
            task.save()
            task.send_update_signal()

        queryset = (
            Task.objects
            .filter(project_id=project.id)
            .filter(assigned_to=None)
            .order_by("pk")
        )

        if is_admin:
            queryset = queryset.select_for_update(skip_locked=True)

            # Get new task first
            task = queryset.filter(is_labeled=False).first()

            # then, task rejected from QA pool
            if project.need_to_qa and task is None:
                task = (
                    queryset
                    .filter(is_in_review=False)
                    .filter(is_in_qc=False)
                    .filter(reviewed_result="rejected")
                    .first()
                )

            # then, new task in QA pool
            if project.need_to_qa and task is None:
                task = (
                    queryset
                    .filter(is_in_review=True)
                    .filter(reviewed_result=None)
                ).first()

            # then, new task in QC pool
            if project.need_to_qa and project.need_to_qc and task is None:
                task = (
                    queryset
                    .filter(is_in_qc=True)
                    .filter(qualified_result=None)
                ).first()
        else:
            # If project has QC pool and current user is QC, find new task in QC pool
            if project.need_to_qa and project.need_to_qc and user_qc:
                task = (
                    Task.objects
                    .select_for_update(skip_locked=True)
                    .filter(project_id=project.id)
                    .filter(assigned_to=None)
                    .filter(is_in_qc=True)
                    .filter(Q(
                        Q(qualified_result=None)
                        & Q(
                            Q(qualified_by=user)
                            | Q(qualified_by=None)
                        )
                    ))
                ).first()
            # else, if project has QA pool and current user is QA, find new task in QA pool
            elif project.need_to_qa and user_qa:
                task = (
                    Task.objects
                    .select_for_update(skip_locked=True)
                    .filter(project_id=project.id)
                    .filter(assigned_to=None)
                    .filter(is_in_review=True)
                    .filter(Q(
                        Q(reviewed_result=None)
                        & Q(
                            Q(reviewed_by=user)
                            | Q(reviewed_by=None)
                        )
                    ))
                ).first()
            # else, find task in Annotator pool
            else:
                # Find new task
                while True:
                    # Find a task without lock DB
                    task = (
                        Task.objects
                        .filter(project_id=project.id)
                        .filter(assigned_to=None)
                        .annotate(my_annotations_count=Count('annotations',
                                                             filter=Q(annotations__completed_by=user)))
                        .filter(Q(
                            Q(
                                Q(is_in_review=False)
                                & Q(is_in_qc=False)
                            )
                            & Q(
                                Q(is_labeled=False)
                                | Q(
                                    Q(reviewed_result="rejected")
                                    & Q(my_annotations_count__gt=0)
                                )
                            )
                        ))
                    ).first()

                    if not task:
                        break

                    # Try to lock the task before update
                    task = Task.objects.select_for_update(skip_locked=True).filter(pk=task.id).first()

                    if task and not task.assigned_to:
                        break

        if task:
            send_audit_log("log-claim-task", {
                "t_id": task.id,
                "t_total_annotations": task.total_annotations,
                "t_is_in_review": task.is_in_review,
                "t_reviewed_by": task.reviewed_by_id,
                "t_is_in_qc": task.is_in_qc,
                "t_qualified_by": task.qualified_by_id,
                "t_assigned_to": task.assigned_to_id,
                "u_id": user.id,
                "u_email": user.email,
                "u_is_superuser": user.is_superuser,
                "u_is_organization_admin": user.is_organization_admin,
                "u_is_qa": user_qa,
                "u_is_qc": user_qc,
            })
            task.assigned_to = user
            task.save()
            task.send_update_signal()

    return task
