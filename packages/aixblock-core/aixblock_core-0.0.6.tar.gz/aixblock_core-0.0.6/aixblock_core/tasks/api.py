"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import threading

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django_dbq.models import Job
from django_filters.rest_framework import DjangoFilterBackend
import drf_yasg.openapi as openapi
from drf_yasg.utils import swagger_auto_schema
from io_storages.functions import get_all_project_storage
from rest_framework import generics, viewsets, views
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from core.permissions import ViewClassPermission, all_permissions
from core.utils.common import (
    DjangoFilterDescriptionInspector,
    get_object_with_check_and_log,
)
from core.utils.params import bool_from_request
from data_manager.api import TaskListAPI as DMTaskListAPI
from data_manager.functions import evaluate_predictions
from data_manager.models import PrepareParams, View
from data_manager.serializers import DataManagerTaskSerializer
from plugins.plugin_centrifuge import publish_message
from projects.models import Project
from tasks.functions import redact_annotation
from tasks.models import Annotation, AnnotationDraft, Prediction, Task
from tasks.serializers import (
    AnnotationDraftSerializer,
    AnnotationSerializer,
    PredictionSerializer,
    TaskSerializer,
    TaskSimpleSerializer,
    TaskQueueRequest,
    TaskAdminViewSerializer
)
from users.models import Notification, User
from users.serializers import NotificationSerializer
from webhooks.models import WebhookAction
from webhooks.utils import (
    api_webhook,
    api_webhook_for_delete,
    emit_webhooks_for_instance,
)
from tasks.models import Task,TaskQueue
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from core.utils.paginate import SetPagination
from organizations.models import OrganizationMember

from ml.models import MLBackend, MLGPU
from model_marketplace.models import ModelMarketplace
from data_export.models import DataExport, Export
from data_export.serializers import ExportDataSerializer
from data_manager.task_queue_function import Task_Manage_Queue
from core.settings.aixblock_core import RQ_QUEUES

from .functions import auto_gen_dataset

logger = logging.getLogger(__name__)


# TODO: fix after switch to api/tasks from api/dm/tasks
@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Tasks'],
        operation_summary='Create task',
        operation_description='Create a new labeling task in AiXBlock.',
        request_body=TaskSerializer))
@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Tasks'],
    operation_summary='Get tasks list',
    operation_description="""
    Retrieve a list of tasks with pagination for a specific view or project, by using filters and ordering.
    """,
    manual_parameters=[
        openapi.Parameter(
            name='view',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_QUERY,
            description='View ID'),
        openapi.Parameter(
            name='project',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_QUERY,
            description='Project ID'),
    ],
))
class TaskListAPI(DMTaskListAPI):
    serializer_class = TaskSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.tasks_view,
        POST=all_permissions.tasks_create,
    )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project',]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        organization_join = OrganizationMember.objects.filter(user_id=self.request.user.id).values_list("organization_id", flat = True)
        return queryset.filter(Q(project__organization=self.request.user.active_organization)|Q(project__organization_id__in=organization_join))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_id = self.request.data.get('project')
        if project_id:
            context['project'] = generics.get_object_or_404(Project, pk=project_id)
        return context

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = generics.get_object_or_404(Project, pk=project_id)
        instance = serializer.save(project=project)
        emit_webhooks_for_instance(self.request.user.active_organization, project, WebhookAction.TASKS_CREATED, [instance])

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Tasks'],
    operation_summary='Get tasks list for Admin',
    operation_description="""
    Retrieve a list of tasks with pagination from admin view.
    """,
    manual_parameters=[
        openapi.Parameter(
            name='project',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_QUERY,
            description='Project ID'),
    ],
))
class TaskListAdminViewAPI(generics.ListAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = (AllowAny, )
    pagination_class = SetPagination
    serializer_class = TaskAdminViewSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project', None)
        if not project:
            return Task.objects.order_by('-id')
        return Task.objects.filter(project=project).order_by('-id')

    def get(self, *args, **kwargs):
        return super(TaskListAdminViewAPI, self).get(*args, **kwargs)

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Tasks'],
        operation_summary='Get task',
        operation_description="""
        Get task data, metadata, annotations and other attributes for a specific labeling task by task ID.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Task ID'
            ),
        ]))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Tasks'],
        operation_summary='Update task',
        operation_description='Update the attributes of an existing labeling task.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Task ID'
            ),
        ],
        request_body=TaskSimpleSerializer))
@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Tasks'],
        operation_summary='Delete task',
        operation_description='Delete a task in AiXBlock. This action cannot be undone!',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Task ID'
            ),
        ],
        ))
class TaskAPI(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.tasks_view,
        PUT=all_permissions.tasks_change,
        PATCH=all_permissions.tasks_change,
        DELETE=all_permissions.tasks_delete,
    )

    @staticmethod
    def prefetch(queryset):
        return queryset.prefetch_related(
            'annotations', 'predictions', 'annotations__completed_by', 'project',
            'io_storages_azureblobimportstoragelink',
            'io_storages_gcsimportstoragelink',
            'io_storages_gdriverimportstoragelink',
            'io_storages_localfilesimportstoragelink',
            'io_storages_redisimportstoragelink',
            'io_storages_s3importstoragelink',
            'file_upload', 'project__ml_backends'
        )

    def get_retrieve_serializer_context(self, request):
        fields = ['drafts', 'predictions', 'annotations']

        return {
            'resolve_uri': True,
            'predictions': 'predictions' in fields,
            'annotations': 'annotations' in fields,
            'drafts': 'drafts' in fields,
            'request': request
        }

    def get(self, request, pk):
        self.task = self.get_object()
        project = self.task.project

        # Check QA role
        # if (project.need_to_qa
        #         and request.user is not None
        #         and (
        #                 (not request.user.is_qa and self.task.is_in_review)
        #                 or (request.user.is_qa and not self.task.is_in_review)
        #         )
        # ):
        #     raise Http404

        context = self.get_retrieve_serializer_context(request)
        context['project'] = project

        # get prediction
        # if (project.evaluate_predictions_automatically or project.show_collab_predictions) \
        #         and not self.task.predictions.exists():
        #     evaluate_predictions([self.task])

        serializer = self.get_serializer_class()(self.task, many=False, context=context, expand=['annotations.completed_by'])
        data = serializer.data
        return Response(data)

    def get_queryset(self):
        review = bool_from_request(self.request.GET, 'review', False)
        selected = {"all": False, "included": [self.kwargs.get("pk")]}
        if review:
            kwargs = {
                'fields_for_evaluation': ['annotators', 'reviewed']
            }
        else:
            kwargs = {'all_fields': True}
        project = self.request.query_params.get('project') or self.request.data.get('project')
        if not project:
            project = Task.objects.get(id=self.request.parser_context['kwargs'].get('pk')).project.id
        return self.prefetch(
            Task.prepared.get_queryset(
                prepare_params=PrepareParams(project=project, selectedItems=selected, request=self.request),
                **kwargs
            ))

    def get_serializer_class(self):
        # GET => task + annotations + predictions + drafts
        if self.request.method == 'GET':
            return DataManagerTaskSerializer

        # POST, PATCH, PUT
        else:
            return TaskSimpleSerializer
    
    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        project = task.project

        # call machine learning api and format response
        if project.evaluate_predictions_automatically:
            for ml_backend in task.project.ml_backends.all():
                ml_backend.predict_tasks([task])

        result = self.get_serializer(task).data

        # use proxy inlining to task data (for credential access)
        result['data'] = task.resolve_uri(result['data'], project)
        return Response(result)

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        project = task.project
        is_qa = None
        is_qc = None
        try:
            from organizations.models import Organization_Project_Permission
            user_role = Organization_Project_Permission.objects.filter(user_id=request.user.id, project_id=project.id, deleted_at__isnull=True).order_by("-id").first()
            is_qa = user_role.is_qa
            is_qc = user_role.is_qc
        except Exception as e:
            print(e)
        # try:
        #     task_annotation_name = f'task_annotation_{project.id}'
        #     # tasl_qa_name = f'task_qa_{project.id}'
        #     # tasl_qc_name = f'task_qc_{project.id}'
        #
        #     connection_params = RQ_QUEUES['custom']
        #
        #     task_annotation = Task_Manage_Queue(task_annotation_name, connection_params)
        #     # task_qa = Task_Manage_Queue(tasl_qa_name, connection_params)
        #     # task_qc = Task_Manage_Queue(tasl_qc_name, connection_params)
        # except Exception as e:
        #     print(e)
            
        # This project enabled QA flow
        if project.need_to_qa and request.user:
            qa_action = request.data['qa_action'] if 'qa_action' in request.data else None
            user_qa = request.user.is_qa if is_qa==None else is_qa
            user_qc = request.user.is_qc if is_qc==None else is_qc 
            
            if qa_action:
                # Annotator complete their task and submit to QA for reviewing
                if qa_action == "review":
                    # if (task.total_annotations == 0
                    #         or len(task.completed_annotations[task.total_annotations - 1].result) == 0):
                    if task.annotations_results[0] == None or len(task.annotations_results[0])==0:
                        return JsonResponse(
                            data={"message": "Please submit at least one annotation before Send to review."},
                            status=403)
                    elif (user_qa or user_qc) and (not request.user.is_superuser and not request.user.is_organization_admin):
                        return JsonResponse(data={"message": "Only annotator users can submit task to QA pool."},
                                            status=403)
                    elif task.assigned_to is not None and task.assigned_to_id != request.user.pk:
                        return JsonResponse(data={"message": "Only assigned user can submit task to QA pool."}, status=403)
                    else:
                        request.data["reviewed_result"] = None
                        # request.data["reviewed_by"] = None
                        request.data["is_in_review"] = True
                        request.data["assigned_to"] = None
                        # try:
                        #     # task_qa.push_task_to_queue(task.id)
                        #     task_annotation.delete_completed_task(task.id)
                        # except:
                        #     print("fail")
                # QA reject the work of annotator, annotator need to rework
                elif qa_action == "reject":
                    if not user_qa and not request.user.is_superuser and not request.user.is_organization_admin:
                        return JsonResponse(data={"message": "You don't have permission to reject task."}, status=403)
                    else:
                        request.data["reviewed_result"] = "rejected"
                        request.data["reviewed_by"] = request.user.id
                        request.data["is_in_review"] = False
                        request.data["assigned_to"] = None
                        # try:
                        #     task_annotation.push_task_to_queue(task.id)
                        # except:
                        #     print("fail")

                        if not project.need_to_qc:
                            request.data["is_in_qc"] = False
                # QA approve the work of annotator, this task will be sent to the QC pool for qualifying
                elif qa_action == "approve":
                    if not user_qa and not request.user.is_superuser and not request.user.is_organization_admin:
                        return JsonResponse(data={"message": "You don't have permission to approve task."}, status=403)
                    else:
                        request.data["reviewed_result"] = "approved"
                        request.data["reviewed_by"] = request.user.id
                        request.data["assigned_to"] = None
                        # try:
                        #     task_qa.delete_completed_task(task.id)
                        # except:
                        #     print("fail")
                        # request.data["qualified_result"] = None
                        # request.data["qualified_by"] = None
                        if project.need_to_qc:
                            request.data["is_in_review"] = False
                            request.data["is_in_qc"] = True
                            request.data["qualified_result"] = None
                            # try:
                            #     task_qc.push_task_to_queue(task.id)
                            # except:
                            #     print("fail")
                # QC unqualify the reviewed result, send back to the QA pool
                elif qa_action == "unqualify":
                    if not user_qc and not request.user.is_superuser and not request.user.is_organization_admin:
                        return JsonResponse(data={"message": "You don't have permission to unqualify task."}, status=403)
                    else:
                        # request.data["reviewed_result"] = None
                        # request.data["reviewed_by"] = None
                        request.data["qualified_result"] = "unqualified"
                        request.data["qualified_by"] = request.user.id
                        request.data["is_in_qc"] = False
                        request.data["reviewed_result"] = None
                        request.data["is_in_review"] = True
                        request.data["assigned_to"] = None
                        # try:
                        #     task_qa.push_task_to_queue(task.id)
                        # except:
                        #     print("fail")
                # QC qualify this task, finished.
                elif qa_action == "qualify":
                    if not user_qc and not request.user.is_superuser and not request.user.is_organization_admin:
                        return JsonResponse(data={"message": "You don't have permission to qualify task."}, status=403)
                    else:
                        request.data["qualified_result"] = "qualified"
                        request.data["qualified_by"] = request.user.id
                        request.data["assigned_to"] = None
                        # try:
                        #     task_qc.delete_completed_task(task.id)
                        # except:
                        #     print("fail")

            users = None

            if not request.user.is_superuser and not request.user.is_organization_admin and project.need_to_qa:
                # Task is in QA pool
                if task.is_in_review:
                    if not user_qa:
                        return JsonResponse(data={"message": "Only QA can update task in QA pool."}, status=403)
                    elif task.reviewed_by and task.reviewed_by.id != request.user.id:
                        return JsonResponse(data={"message": "This task is handling by another user."}, status=403)
                # QC turned on, and task is in QC pool
                elif project.need_to_qc and task.is_in_qc:
                    if not user_qc:
                        return JsonResponse(data={"message": "Only QC can update task in QC pool."}, status=403)
                    elif task.qualified_by and task.qualified_by.id != request.user.id:
                        return JsonResponse(data={"message": "This task is handling by another user."}, status=403)
                # Task is in Working pool
                elif not task.is_in_review and not task.is_in_qc:
                    if user_qa or user_qc:
                        return JsonResponse(data={"message": "This task is in working pool, only annotators can update it."}, status=403)

                    users = [x.completed_by.id for x in task.annotations.all() if x.completed_by is not None]

                    if task.reviewed_result == "rejected" and request.user.id not in users:
                        return JsonResponse(data={"message": "This task is handling by another user."}, status=403)

            response = super(TaskAPI, self).patch(request, *args, **kwargs)

            if project.export_dataset:
                t = threading.Thread(target=auto_gen_dataset, args=(self, project, request.GET))
                t.start()

            if qa_action == "approve" or  qa_action == "reject" or qa_action == "unqualify" or qa_action == "qualify":
                if not users:
                    users = [x.completed_by for x in task.annotations.all() if x.completed_by is not None]

                view = View.objects.filter(project=project).order_by("id").first()
                actions = {
                    "approve": "approved",
                    "reject": "rejected",
                    "qualify": "qualified",
                    "unqualify": "unqualified",
                }

                if qa_action == "unqualify" or qa_action == "qualify":
                    if task.reviewed_by:
                        users.append(task.reviewed_by)

                for user in users:
                    notification = Notification(
                        content=f"Your task #{task.id} has been {actions[qa_action]}",
                        user=user,
                        link=f"/projects/{task.project_id}/data?task={task.id}&tab={view.id}",
                    )

                    notification.save()
                    serializer = NotificationSerializer(notification)

                    publish_message(
                        channel=f"user/{user.id}/notification",
                        data=serializer.data,
                    )

            # task_qa.push_task_to_queue(task.id)
            task.send_update_signal()
            return response

            # if not request.user.is_superuser:
            #     # Non-QA user can not update task in review
            #     if not request.user.is_qa and task.is_in_review:
            #         return JsonResponse(data={"message": "This task is in review, you can not update it."}, status=403)
            #     # Non-QC user can not update task in QC
            #     if not request.user.is_qc and task.is_in_qc:
            #         return JsonResponse(data={"message": "This task is in qualifying, you can not update it."}, status=403)
            #     # QA can not send task to review pool
            #     elif 'is_in_review' in request.data and request.data['is_in_review'] and request.user.is_qa:
            #         return JsonResponse(data={"message": "Only non-QA user can submit task to QA pool."}, status=403)
            #     # QC can not send task to QC pool
            #     elif 'is_in_qc' in request.data and request.data['is_in_qc'] and request.user.is_qc:
            #         return JsonResponse(data={"message": "Only non-QC user can submit task to QC pool."}, status=403)
            #     # Non-QA users can not approve/reject task
            #     elif ('reviewed_result' in request.data
            #           and (request.data['reviewed_result'] == "approved" or request.data['reviewed_result'] == "rejected")
            #           and not request.user.is_qa
            #     ):
            #         return JsonResponse(data={"message": "Only user with QA role can review tasks."}, status=403)
            #     # Non-QC users can not qualify/unqualify task
            #     elif ('qualified_result' in request.data
            #           and (request.data['qualified_result'] == "qualified" or request.data['qualified_result'] == "unqualified")
            #           and not request.user.is_qc
            #     ):
            #         return JsonResponse(data={"message": "Only user with QC role can qualify tasks."}, status=403)
            #
            # # Task with empty annotations list can not be sent to review pool
            # if ('is_in_review' in request.data
            #         and request.data['is_in_review']
            #         and (task.total_annotations == 0
            #              or len(task.completed_annotations[0].result) == 0
            #         )
            # ):
            #     return JsonResponse(data={"message": "Please submit at least one annotation before Send to review."}, status=403)
            #
            # if not task.is_in_qc and not task.is_in_review and "is_in_review" in request.data and request.data["is_in_review"]:
            #     request.data["reviewed_result"] = None
            #     request.data["reviewed_by"] = None
            #
            # if not task.is_in_qc and "is_in_qc" in request.data and request.data["is_in_qc"]:
            #     request.data["qualified_result"] = None
            #     request.data["qualified_by"] = None
            #
            # if task.is_in_qc and "qualified_result" in request.data:
            #     request.data["qualified_by"] = request.user.id

        return super(TaskAPI, self).patch(request, *args, **kwargs)

    @api_webhook_for_delete(WebhookAction.TASKS_DELETED)
    def delete(self, request, *args, **kwargs):
        return super(TaskAPI, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(TaskAPI, self).put(request, *args, **kwargs)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Get annotation by its ID',
        operation_description='Retrieve a specific annotation for a task using the annotation result ID.',
        ))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Update annotation',
        operation_description='Update existing attributes on an annotation.',
        request_body=AnnotationSerializer))
@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Delete annotation',
        operation_description='Delete an annotation. This action can\'t be undone!',
        ))
class AnnotationAPI(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        PUT=all_permissions.annotations_change,
        PATCH=all_permissions.annotations_change,
        DELETE=all_permissions.annotations_delete,
    )

    serializer_class = AnnotationSerializer
    queryset = Annotation.objects.all()

    def perform_destroy(self, annotation):
        task = annotation.task
        annotation.delete()
        task.send_update_signal()

    def update(self, request, *args, **kwargs):
        # save user history with annotator_id, time & annotation result
        annotation_id = self.kwargs['pk']
        annotation = get_object_with_check_and_log(request, Annotation, pk=annotation_id)

        task = annotation.task
        if self.request.data.get('ground_truth'):
            task.ensure_unique_groundtruth(annotation_id=annotation.id)
        task.update_is_labeled()
        task.save()  # refresh task metrics

        result = super(AnnotationAPI, self).update(request, *args, **kwargs)

        task.update_is_labeled()
        task.save(update_fields=['updated_at'])  # refresh task metrics
        task.send_update_signal()
        return result

    def get(self, request, *args, **kwargs):
        return super(AnnotationAPI, self).get(request, *args, **kwargs)

    @api_webhook(WebhookAction.ANNOTATION_UPDATED)
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(AnnotationAPI, self).put(request, *args, **kwargs)

    @api_webhook(WebhookAction.ANNOTATION_UPDATED)
    def patch(self, request, *args, **kwargs):
        return super(AnnotationAPI, self).patch(request, *args, **kwargs)

    @api_webhook_for_delete(WebhookAction.ANNOTATIONS_DELETED)
    def delete(self, request, *args, **kwargs):
        return super(AnnotationAPI, self).delete(request, *args, **kwargs)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Get all task annotations',
        operation_description='List all annotations for a task.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='Task ID'),
        ],
        ))
@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Create annotation',
        operation_description="""
        Add annotations to a task like an annotator does. The content of the result field depends on your 
        labeling configuration. For example, send the following data as part of your POST 
        request to send an empty annotation with the ID of the user who completed the task:
        
        ```json
        {
        "result": {},
        "was_cancelled": true,
        "ground_truth": true,
        "lead_time": 0,
        "task": 0
        "completed_by": 123
        } 
        ```
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='Task ID'),
        ],
        request_body=AnnotationSerializer
        ))
class AnnotationsListAPI(generics.ListCreateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_create,
    )

    serializer_class = AnnotationSerializer

    def get(self, request, *args, **kwargs):
        return super(AnnotationsListAPI, self).get(request, *args, **kwargs)

    @api_webhook(WebhookAction.ANNOTATION_CREATED)
    def post(self, request, *args, **kwargs):
        return super(AnnotationsListAPI, self).post(request, *args, **kwargs)

    def get_queryset(self):
        task = generics.get_object_or_404(Task.objects.for_user(self.request.user), pk=self.kwargs.get('pk', 0))
        return Annotation.objects.filter(Q(task=task) & Q(was_cancelled=False)).order_by('pk')

    def delete_draft(self, draft_id, annotation_id):
        return AnnotationDraft.objects.filter(id=draft_id).delete()

    def perform_create(self, ser):
        task = get_object_with_check_and_log(self.request, Task, pk=self.kwargs['pk'])
        # annotator has write access only to annotations and it can't be checked it after serializer.save()
        user = self.request.user

        # updates history
        result = ser.validated_data.get('result')
        extra_args = {'task_id': self.kwargs['pk']}

        # save stats about how well annotator annotations coincide with current prediction
        # only for finished task annotations
        if result is not None:
            prediction = Prediction.objects.filter(task=task, model_version=task.project.model_version)
            if prediction.exists():
                prediction = prediction.first()
                prediction_ser = PredictionSerializer(prediction).data
            else:
                logger.debug(f'User={self.request.user}: there are no predictions for task={task}')
                prediction_ser = {}
            # serialize annotation
            extra_args.update({
                'prediction': prediction_ser,
            })

        if 'was_cancelled' in self.request.GET:
            extra_args['was_cancelled'] = bool_from_request(self.request.GET, 'was_cancelled', False)

        if 'completed_by' not in ser.validated_data:
            extra_args['completed_by'] = self.request.user

        # create annotation
        logger.debug(f'User={self.request.user}: save annotation')
        annotation = ser.save(**extra_args)
        logger.debug(f'Save activity for user={self.request.user}')
        self.request.user.activity_at = timezone.now()
        self.request.user.save()

        # Release task if it has been taken at work (it should be taken by the same user, or it makes sentry error
        logger.debug(f'User={user} releases task={task}')
        task.release_lock(user)

        # if annotation created from draft - remove this draft
        draft_id = self.request.data.get('draft_id')
        if draft_id is not None:
            logger.debug(f'Remove draft {draft_id} after creating annotation {annotation.id}')
            self.delete_draft(draft_id, annotation.id)

        if self.request.data.get('ground_truth'):
            annotation.task.ensure_unique_groundtruth(annotation_id=annotation.id)

        if task.project.show_collab_predictions and not task.project.need_to_qa and not task.project.need_to_qc:
            t = threading.Thread(target=auto_gen_dataset, args=(self, task.project, self.request.GET))
            t.start()

        task.send_update_signal()


class AnnotationDraftListAPI(generics.ListCreateAPIView):

    parser_classes = (JSONParser, MultiPartParser, FormParser)
    serializer_class = AnnotationDraftSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_create,
    )
    queryset = AnnotationDraft.objects.all()
    swagger_schema = None

    def filter_queryset(self, queryset):
        task_id = self.kwargs['pk']
        return queryset.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs['pk']
        annotation_id = self.kwargs.get('annotation_id')
        user = self.request.user
        logger.debug(f'User {user} is going to create draft for task={task_id}, annotation={annotation_id}')
        serializer.save(
            task_id=self.kwargs['pk'],
            annotation_id=annotation_id,
            user=self.request.user
        )


class AnnotationDraftAPI(generics.RetrieveUpdateDestroyAPIView):

    parser_classes = (JSONParser, MultiPartParser, FormParser)
    serializer_class = AnnotationDraftSerializer
    queryset = AnnotationDraft.objects.all()
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        PUT=all_permissions.annotations_change,
        PATCH=all_permissions.annotations_change,
        DELETE=all_permissions.annotations_delete,
    )
    swagger_schema = None


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['Predictions'],
    operation_summary="List predictions",
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="List all predictions and their IDs.",
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    tags=['Predictions'],
    operation_summary="Create prediction",
    operation_description="Create a prediction for a specific task.",
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['Predictions'],
    operation_summary="Get prediction details",
    operation_description="Get details about a specific prediction by its ID.",
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='Prediction ID'),
    ],
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['Predictions'],
    operation_summary="Put prediction",
    operation_description="Overwrite prediction data by prediction ID.",
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='Prediction ID'),
    ],
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    tags=['Predictions'],
    operation_summary="Update prediction",
    operation_description="Update prediction data by prediction ID.",
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='Prediction ID'),
    ],
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    tags=['Predictions'],
    operation_summary="Delete prediction",
    operation_description="Delete a prediction by prediction ID.",
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='Prediction ID'),
    ],
))
class PredictionAPI(viewsets.ModelViewSet):
    serializer_class = PredictionSerializer
    permission_required = all_permissions.predictions_any
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'task__project']

    def get_queryset(self):
        organization_join = OrganizationMember.objects.filter(user_id=self.request.user.id).values_list("organization_id", flat = True)
        return Prediction.objects.filter(Q(task__project__organization=self.request.user.active_organization) | Q(project__organization_id__in=organization_join))


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Convert annotation to draft',
        operation_description='Convert annotation to draft',
        ))
class AnnotationConvertAPI(views.APIView):
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_change
    )

    def process_intermediate_state(self, annotation, draft):
        pass

    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        annotation = get_object_with_check_and_log(request, Annotation, pk=self.kwargs['pk'])
        organization = annotation.task.project.organization
        project = annotation.task.project
        pk = annotation.pk

        with transaction.atomic():
            draft = AnnotationDraft.objects.create(
                result=annotation.result,
                lead_time=annotation.lead_time,
                task=annotation.task,
                annotation=None,
                user=request.user,
            )

            self.process_intermediate_state(annotation, draft)

            annotation.delete()

        emit_webhooks_for_instance(organization, project, WebhookAction.ANNOTATIONS_DELETED, [pk])
        data = AnnotationDraftSerializer(instance=draft).data
        return Response(status=201, data=data)

# @method_decorator(name='get', decorator=swagger_auto_schema(
#         tags=['Task Queue'],
#         operation_summary='Retrieve my queue',
#         operation_description=''
#     ))
# class TaskQueueListAPI(generics.mixins.ListModelMixin,APIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     queryset = TaskQueue.objects.all()
#     permission_classes = (IsAuthenticated,)
#     # serializer_class = UserSerializer
#     def get_queryset(self):
        
        
#         return TaskQueue.objects.filter()
    
#     def filter_queryset(self, queryset):
#         return TaskQueue.objects.all()
   
#     def get(self, request, *args, **kwargs):
#         _status = kwargs['status']
#         _project_id =  kwargs['project_id']
#         print(f"_status:{_status}")
#         print(f"_project_id:{_project_id}")
#         print(f"request:{request}")
#         print(f"args:{args}")
#         print(f"kwargs:{kwargs}")
#         return Response(
#             list(TaskQueue.objects.filter(status=_status).values('id', 'project_id', 'task_id', 'try_count','max_tries','priority','status').order_by('-id')[:10])
#         )

# @method_decorator(
#         name='post',
#         decorator=swagger_auto_schema(
#             tags=['Task Queue'],
#             operation_summary='',
#             operation_description="""
            
#             """,
#             manual_parameters=[
                
#             ],
#             request_body=TaskQueueRequest,
#             responses={
#                 200: openapi.Response(title='Task queue OK', description='Task queue has succeeded.'),
#             },
#         )
#     )
# class TaskQueueAPI(APIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     queryset = TaskQueue.objects.all()
#     permission_classes = (IsAuthenticated,)
   
   
#     def post(self, request, *args, **kwargs):
#         j_obj = json.loads(request.body)
#         # print(j_obj )
#         user = request.user
#         item =TaskQueue.objects.filter(task_id=int(j_obj["task_id"]),project_id=int(j_obj["project_id"])).first()
#         if int(j_obj["id"]) > 0 :
#             item =TaskQueue.objects.filter(id=int(j_obj["id"])).first()
#             item.project_id=j_obj["project_id"]
#             item.task_id=j_obj["task_id"]
#             item.status=j_obj["status"]
#             item.try_count=j_obj["try_count"]
#             item.max_tries=j_obj["max_tries"]
#             item.priority=j_obj["priority"]
#             item.save()
#         # elif item != None :
#         #     # item =TaskQueue.objects.filter(id=int(j_obj["id"])).first()
#         #     item.project_id=j_obj["project_id"]
#         #     item.task_id=j_obj["task_id"]
#         #     item.status=j_obj["status"]
#         #     item.try_count=j_obj["try_count"]
#         #     item.max_tries=j_obj["max_tries"]
#         #     item.priority=j_obj["priority"]
#         #     item.save()
#         else:
#             TaskQueue.objects.create(
#                     user_id=user.id,
#                     project_id=j_obj["project_id"],
#                     task_id=j_obj["task_id"],
#                     status=j_obj["status"],
#                     try_count=j_obj["try_count"],
#                     max_tries=j_obj["max_tries"],
#                     priority=j_obj["priority"],
#                 )
#         # print(result )
#         return Response({"msg":"done"}, status=200)


@method_decorator(
        name='post',
        decorator=swagger_auto_schema(
            tags=['Task Lock'],
            operation_summary="Lock a task",
            operation_description="""
            """,
            manual_parameters=[],
            responses={
                200: openapi.Response(title='OK', description='Task has been locked.'),
            },
        )
    )
class TaskLockAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        task_id = kwargs["pk"]
        task: Task = self.queryset.filter(pk=task_id).first()

        if task is None:
            return Response({"message": "Task not found"}, status=404)

        user = request.user

        if not user.is_superuser and not user.is_staff and task.assigned_to and task.assigned_to != user:
            return Response({"message": "This task has been assigned to another user"}, status=403)

        if task.set_lock(request.user):
            try:
                publish_message(
                    channel=f"task/{task.id}",
                    data={
                        "command": "lock",
                        "user_id": request.user.id,
                    }
                )
            except Exception as e:
                logging.error(e)

            return Response({"message": "Task locked"}, status=200)
        else:
            return Response({"message": "Task has been locked by other user"}, status=403)


@method_decorator(
        name='post',
        decorator=swagger_auto_schema(
            tags=['Task Lock'],
            operation_summary="Release a task",
            operation_description="""
            """,
            manual_parameters=[],
            responses={
                200: openapi.Response(title='OK', description='Task has been released.'),
            },
        )
    )
class TaskReleaseAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        task_id = kwargs["pk"]
        task = self.queryset.filter(pk=task_id).first()

        if task is None:
            return Response({"message": "Task not found"}, status=404)

        if task.release_lock(request.user):
            try:
                publish_message(
                    channel=f"task/{task.id}",
                    data={
                        "command": "release",
                        "user_id": request.user.id,
                    },
                )
            except Exception as e:
                logging.error(e)

            return Response({"message": "Task has been released"}, status=200)
        else:
            return Response({"message": "Can not release this task"}, status=403)


@method_decorator(
        name='post',
        decorator=swagger_auto_schema(
            tags=['Assign tasks'],
            operation_summary='Assign a task to an user',
            operation_description="""
            """,
            responses={
                200: openapi.Response(title='Success', description='Task assigned to user successfully'),
                403: openapi.Response(title='Forbidden', description='Only admin/staff can assign task to a specific '
                                                                     'user. User can not park more than the limit.'
                                                                     'Can not assign a task of another user.'),
                404: openapi.Response(title='Not found', description='Task/user not found'),
            },
        )
    )
class TaskAssignAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            task = self.queryset.select_for_update().prefetch_related("project").get(pk=pk)

            if not Task:
                return Response({"message": "Task not found"}, status=404)

            if task.assigned_to is not None and not request.user.is_superuser and not request.user.is_staff:
                return Response({"message": "This task has been assigned to another user"}, status=403)

            if request.data.has("user_id"):
                if request.user.is_superuser or request.user.is_staff:
                    user_id = request.data.get("user_id")
                    user = User.objects.get(id=user_id)

                    if not User:
                        return Response({"message": f"User #{user_id} not found"}, status=404)
                else:
                    return Response({"message": "Only admin/staff can assign task to a specific user"}, status=403)
            else:
                user = request.user

            if task.project.max_parked_tasks > 0 and not request.user.is_superuser and not request.user.is_staff:
                if self.queryset.filter(assigned_to=user).count() >= task.project.max_parked_tasks:
                    return Response({"message": f"You can not park more than {task.project.max_parked_tasks} task(s)"},
                                    status=403)

            task.assigned_to = user
            task.save()
            task.send_update_signal()
            return Response({"message": "Success"}, status=200)


@method_decorator(
        name='post',
        decorator=swagger_auto_schema(
            tags=['Assign tasks'],
            operation_summary='Unassign a task of an user',
            operation_description="""
            """,
            responses={
                200: openapi.Response(title='Success', description='Task assigned to user successfully'),
                403: openapi.Response(title='Forbidden', description='Can not unassign the task of other users'),
                404: openapi.Response(title='Not found', description='Task not found'),
            },
        )
    )
class TaskUnassignAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            task = self.queryset.select_for_update().get(pk=pk)

            if not Task:
                return Response({"message": "Task not found"}, status=404)

            if not request.user.is_superuser and not request.user.is_staff and request.user != task.assigned_to:
                return Response({"message": "You can not unassign the task of other users"}, status=403)

            task.assigned_to = None
            task.save()
            task.send_update_signal()
            return Response({"message": "Success"}, status=200)


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Annotations'],
        operation_summary='Redact audio',
        operation_description='Redact audio',
        ))
class AnnotationRedactAPI(views.APIView):
    permission_required = ViewClassPermission(
        POST=all_permissions.annotations_change
    )

    def post(self, request, *args, **kwargs):
        annotation = get_object_with_check_and_log(request, Annotation, pk=self.kwargs['pk'])

        if not annotation.task.is_data_optimized:
            return Response(status=200, data={
                "detail": "The data for this task is being optimized. Please try again after the data has been optimized.",
            })

        Job.objects.create(name="redact_audio", workspace={
            "annotation_pk": annotation.pk,
        })

        return Response(status=200, data={
            "detail": "Your audio will be redacted soon",
        })
