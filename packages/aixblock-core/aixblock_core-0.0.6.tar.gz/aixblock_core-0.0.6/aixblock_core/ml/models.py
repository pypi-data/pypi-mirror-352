"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from core.utils.common import safe_float, conditional_atomic, load_func

from ml.api_connector import MLApi
from projects.models import Project
from tasks.models import Prediction
from tasks.serializers import TaskSimpleSerializer, PredictionSerializer
from webhooks.serializers import WebhookSerializer, Webhook

logger = logging.getLogger(__name__)

MAX_JOBS_PER_PROJECT = 1

InteractiveAnnotatingDataSerializer = load_func(settings.INTERACTIVE_DATA_SERIALIZER)


class MLBackendState(models.TextChoices):
    CONNECTED = 'CO', _('Connected')
    DISCONNECTED = 'DI', _('Disconnected')
    ERROR = 'ER', _('Error')
    TRAINING = "TR", _("Training")
    STOP_TRAINING = "STR", _("Stop Training")
    PREDICTING = 'PR', _('Predicting')


class MLNetwork(models.Model):
    project_id = models.IntegerField(_("project_id"), null=True)
    name = models.TextField(_("name"), null=True, default="default")
    model_id = models.IntegerField(_("model_id"), null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)
    class TYPE_NETWORK(models.TextChoices):
        TRAINING = "training", _("Training")
        INFERENCE = "inference", _("Inference")

    type = models.CharField(
        _("type"),
        max_length=100,
        choices=TYPE_NETWORK.choices,
        default=TYPE_NETWORK.TRAINING,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = "default"
        super(MLNetwork, self).save(*args, **kwargs)


class MLBackend(models.Model):
    state = models.CharField(
        max_length=3,
        choices=MLBackendState.choices,
        default=MLBackendState.DISCONNECTED,
    )
    is_interactive = models.BooleanField(
        _('is_interactive'),
        default=False,
        help_text=("Used to interactively annotate tasks. "
                   'If true, model returns one list with results')
    )
    url = models.TextField(
        _('url'),
        help_text='URL for the machine learning model server',
    )
    error_message = models.TextField(
        _('error_message'),
        blank=True,
        null=True,
        help_text='Error message in error state',
    )
    title = models.TextField(
        _('title'),
        blank=True,
        null=True,
        default='default',
        help_text='Name of the machine learning backend',
    )
    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        default='',
        help_text='Description for the machine learning backend',
    )
    model_version = models.TextField(
        _('model version'),
        blank=True,
        null=True,
        default='',
        help_text='Current model version associated with this machine learning backend',
    )
    timeout = models.FloatField(
        _('timeout'),
        blank=True,
        default=100.0,
        help_text='Response model timeout',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ml_backends',
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True)
    auto_update = models.BooleanField(
        _('auto_update'),
        default=True,
        help_text='If false, model version is set by the user, if true - getting latest version from backend.'
    )
    is_deploy = models.BooleanField(_('is_deploy'), default=False, null=True)

    class INSTALL_STATUS(models.TextChoices):
        INSTALLING = "installing", _("installing")
        REINSTALLING = "reinstalling", _("reinstalling")
        COMPLEATED = "compleated", _("compleated")
        FAILED = "failed", _("failed")

    install_status = models.CharField(
        _("deleted_by"),
        max_length=64,
        choices=INSTALL_STATUS.choices,
        default=INSTALL_STATUS.INSTALLING,
        null=True,
    )

    mlnetwork = models.ForeignKey(MLNetwork, on_delete=models.CASCADE, related_name='ml_backends', null=True, blank=True)

    ram = models.FloatField(
        _('ram'),
        blank=True,
        default=0.0,
        null=True
    )

    config = models.JSONField(
        _("config"),
        blank=True,
        null=True,
        help_text="config for ml",
    )

    def __str__(self):
        return f'{self.title} (id={self.id}, url={self.url})'

    # @staticmethod
    # def healthcheck_(url):
    #     return MLApi(url=url).health()

    def has_permission(self, user):
        return self.project.has_permission(user)

    @staticmethod
    def setup_(url, project, model_version=None, compute_id = None):
        api = MLApi(url=url)
        if not isinstance(project, Project):
            project = Project.objects.get(pk=project)
        return api.setup(project, model_version=model_version, compute_id=compute_id)

    # def healthcheck(self):
    #     return self.healthcheck_(self.url)

    def setup(self, compute_id= None):
        return self.setup_(
            self.url,
            self.project,
            None if self.auto_update else self.model_version,
            compute_id,
        )

    @property
    def api(self):
        return MLApi(url=self.url, timeout=self.timeout)

    @property
    def not_ready(self):
        return self.state not in (MLBackendState.CONNECTED, MLBackendState.ERROR)

    def update_state(self, compute_id = None):
        # if self.healthcheck().is_error:
        #     self.state = MLBackendState.CONNECTED
        # else:
        try:
            setup_response = self.setup(compute_id)
            if setup_response.is_error:
                logger.info(f'ML backend responds with error: {setup_response.error_message}')
                self.state = MLBackendState.ERROR
                self.error_message = setup_response.error_message
            else:
                self.state = MLBackendState.CONNECTED
                model_version = setup_response.response.get('model_version')
                logger.info(f'ML backend responds with success: {setup_response.response}')
                if self.auto_update:
                    # Ensure model_version is a string before logging
                    model_version_str = str(model_version)
                    logger.debug(f'Changing model version: {self.model_version} -> {model_version_str}')
                    self.model_version = model_version_str
                self.error_message = None
            self.save()
        except Exception as e:
            logger.error(f'Exception occurred while updating state: {e}')
            self.state = MLBackendState.ERROR
            self.error_message = str(e)
            self.save()

    def train(self, token=None, master_address = None, master_port = None, rank = None, world_size=None, workers=None, ps=None, configs = [], ml_backend_id=None):
        train_response = self.api.train(
            self.project,
            token=token,
            master_address=master_address,
            master_port=master_port,
            rank=rank,
            world_size=world_size,
            workers=workers,
            ps=ps,
            configs=configs,
            ml_backend_id=ml_backend_id
        )
        if train_response.is_error:
            self.state = MLBackendState.ERROR
            self.error_message = train_response.error_message
        else:
            self.state = MLBackendState.TRAINING
            current_train_job = train_response.response.get('job')
            if current_train_job:
                MLBackendTrainJob.objects.create(job_id=current_train_job, ml_backend=self)
        self.save()

    def stop_train(self, token=None):
        train_response = self.api.stop_train(self.project, token=token)
        if train_response.is_error:
            self.state = MLBackendState.ERROR
            self.error_message = train_response.error_message
            self.save()
        else:
            self.state = MLBackendState.CONNECTED

            current_train_job = train_response.response.get("job")
            if current_train_job:
                # update training job
                # MLBackendTrainJob.objects.create(
                #     job_id=current_train_job, ml_backend=self
                # )
                pass
        self.save()

    def get_tensorboard(self, token=None):
        train_response = self.api.get_tensorboard(self.project, token=token)
        if train_response.is_error:
            self.state = MLBackendState.ERROR
            self.error_message = train_response.error_message
            self.save()
        else:
            self.state = MLBackendState.CONNECTED

            current_train_job = train_response.response.get("job")
            if current_train_job:
                # update training job
                # MLBackendTrainJob.objects.create(
                #     job_id=current_train_job, ml_backend=self
                # )
                pass
        self.save()
        return train_response

    def get_dashboard(self, token=None):
        dashboard_res = self.api.get_dashboard(self.project, token=token)
        if dashboard_res.is_error:
            self.state = MLBackendState.ERROR
            self.error_message = dashboard_res.error_message
            self.save()
        else:
            self.state = MLBackendState.CONNECTED

            current_train_job = dashboard_res.response.get("job")
            if current_train_job:
                # update training job
                # MLBackendTrainJob.objects.create(
                #     job_id=current_train_job, ml_backend=self
                # )
                pass
        self.save()
        if dashboard_res and dashboard_res.response:
            result = dashboard_res.response.get("results")
            url = result.get("Share_url")
            return url
        return ""

    def predict_tasks(self, tasks, request=None):
        self.update_state()
        if self.not_ready:
            logger.debug(f'ML backend {self} is not ready')
            return

        if isinstance(tasks, list):
            from tasks.models import Task

            tasks = Task.objects.filter(id__in=[task.id for task in tasks])

        tasks_ser = TaskSimpleSerializer(tasks, many=True).data
        ml_api_result = self.api.make_predictions(tasks_ser, self.model_version, self.project)
        if request:
            responses = ml_api_result
            for task, response in zip(tasks_ser, responses):
                if 'result' not in response:
                    logger.info(
                        f"ML backend returns an incorrect prediction, it should be a dict with the 'result' field:"
                        f" {response}"
                    )
                    return
                
                from tasks.serializers import AnnotationSerializer
                from core.utils.params import bool_from_request
                from django.utils import timezone
                import re
                import json
                
                try:
                    annotations_project = None
                    project_id = task['project']
                    project = Project.objects.filter(id=project_id).first()
                    label_config = project.label_config
                    match = re.search(r'<!--(.*?)-->', label_config, re.DOTALL)

                    if match:
                        json_data = match.group(1).strip()  # Lấy nội dung bên trong dấu <!-- ... -->
                        try:
                            data_dict = json.loads(json_data)  # Chuyển đổi chuỗi JSON thành dictionary
                            annotations_project = data_dict.get("annotations", [])
                        except json.JSONDecodeError:
                            print("Không thể parse chuỗi JSON.")
                    else:
                        print("Không tìm thấy annotations trong label_config.")
                except Exception as e:
                    print(e)

                results = []
                for res in response['result']:
                    if "type" in res and res["type"] == "polygonlabels":
                        type = "polygon"
                        label = res["value"]["polygonlabels"][0]
                        normalized_points = [
                                {
                                    "x": point[0] / 100,  # chuyển thành tỉ lệ dựa trên 100
                                    "y": point[1] / 100
                                }
                                for point in res["value"]["points"]
                            ]
                        
                        results.append({
                            "regionType": type,
                            "id": "9893144574896164",
                            "classification": label,
                            "color": "#FF0000",
                            "points": normalized_points
                        })

                    elif "type" in res and res["type"] == "rectanglelabels":
                        type = "bounding-box"
                        label = res["value"]["rectanglelabels"][0]
                        # points = res["value"]["points"]

                        original_width = res["original_width"]
                        original_height = res["original_height"]

                        height = res["value"]['height'] / 100
                        width = res["value"]['width'] / 100
                        centerX = res["value"]['x'] / 100 + width / 2
                        centerY = res["value"]['y'] / 100 + height / 2

                        results.append({
                            "regionType": type,
                            "id": "6857710453135393",
                            "centerX": centerX,
                            "centerY":centerY,
                            "width": width,
                            "height": height,
                            "classification": label,
                            "color": "#FFFFFF"
                        })

                    elif "type" in res and res["type"] == "videorectangle":
                        results.append(res)
                    
                    elif "type" not in res and res['result'][0]["type"] == "textarea":
                        if annotations_project:
                            res['result'][0]['type'] = annotations_project[0]['result'][0]['type']
                            res['result'][0]['id'] = annotations_project[0]['result'][0]['id']
                            res['result'][0]['from_name'] = annotations_project[0]['result'][0]['from_name']
                            res['result'][0]['to_name'] = annotations_project[0]['result'][0]['to_name']
                        else:
                            if "Text Summarization" in project.label_config_title:
                                task_name = "text-generation"
                            elif "Named Entity Recognition" in project.label_config_title:
                                task_name = "ner"
                                model_id = "SKT27182/Name_Entity_Recognizer"
                            elif "Question Answering" in project.label_config_title:
                                question = task["data"]["text"]
                                answer = res['result'][0]["value"]["text"][0]
                                start_position = question.find(answer)
                                # Kiểm tra nếu tìm thấy
                                if start_position != -1:
                                    # Tính vị trí cuối
                                    end_position = start_position + len(answer) - 1
                                    print("Vị trí đầu:", start_position)
                                    print("Vị trí cuối:", end_position)
                                else:
                                    print("Không tìm thấy đoạn text.")

                                res['result'][0]['type'] = "labels"
                                res['result'][0]['id'] = "Jvr123"
                                res['result'][0]['from_name'] = "answer"
                                res['result'][0]['to_name'] = "text"
                                res['result'][0]["value"]['text'] = answer
                                res['result'][0]["value"]['labels'] = ["Answer"]
                                res['result'][0]["value"]['start'] = start_position
                                res['result'][0]["value"]['end'] = end_position

                            # elif "Machine Translation" in project.label_config_title:
                            #     task_name = "translation"
                            # else:
                            #     task_name = "text-generation"

                        results.append(res['result'][0])

                user = request.user
                ser = AnnotationSerializer(data={"result": results})
                cd = ser.is_valid()
            
                result = ser.validated_data.get('result')
                extra_args = {'task_id': task['id']}

                # save stats about how well annotator annotations coincide with current prediction
                # only for finished task annotations
                # if result is not None:
                #     prediction = Prediction.objects.filter(task=task, model_version=task.project.model_version)
                #     if prediction.exists():
                #         prediction = prediction.first()
                #         prediction_ser = PredictionSerializer(prediction).data
                #     else:
                #         logger.debug(f'User={self.request.user}: there are no predictions for task={task}')
                #         prediction_ser = {}
                # serialize annotation
                extra_args.update({
                    'prediction': {},
                })

                if 'was_cancelled' in request.GET:
                    extra_args['was_cancelled'] = bool_from_request(request.GET, 'was_cancelled', False)

                if 'completed_by' not in ser.validated_data:
                    extra_args['completed_by'] = request.user

                # create annotation
                logger.debug(f'User={request.user}: save annotation')
                annotation = ser.save(**extra_args)
                logger.debug(f'Save activity for user={request.user}')
                request.user.activity_at = timezone.now()
                request.user.save()

            return
        
        # if ml_api_result.is_error:
        #     logger.info(f'Prediction not created for project {self}: {ml_api_result.error_message}')
        #     return

        # if not (isinstance(ml_api_result.response, dict) and 'results' in ml_api_result.response):
        #     logger.info(f'ML backend returns an incorrect response, it should be a dict: {ml_api_result.response}')
        #     return

        # responses = ml_api_result.response['results']
        # if len(responses) == 0:
        #     logger.warning(f'ML backend returned empty prediction for project {self}')
        #     return

        # ML Backend doesn't support batch of tasks, do it one by one
        # elif len(responses) == 1 and len(tasks) != 1:
        #     logger.warning(
        #         f"'ML backend '{self.title}' doesn't support batch processing of tasks, "
        #         f"switched to one-by-one task retrieval"
        #     )
        #     for task in tasks:
        #         self.__predict_one_task(task)
        #     return

        # # wrong result number
        # elif len(responses) != len(tasks_ser):
        #     logger.warning(f'ML backend returned response number {len(responses)} != task number {len(tasks_ser)}')

        # predictions = []
        # for task, response in zip(tasks_ser, responses):
        #     if 'result' not in response:
        #         logger.info(
        #             f"ML backend returns an incorrect prediction, it should be a dict with the 'result' field:"
        #             f" {response}"
        #         )
        #         return

        #     predictions.append(
        #         {
        #             'task': task['id'],
        #             'result': response['result'],
        #             'score': response.get('score'),
        #             'model_version': ml_api_result.response.get('model_version', self.model_version),
        #         }
        #     )
        # with conditional_atomic():
        #     prediction_ser = PredictionSerializer(data=predictions, many=True)
        #     prediction_ser.is_valid(raise_exception=True)
        #     prediction_ser.save()

    def __predict_one_task(self, task):
        self.update_state()
        if self.not_ready:
            logger.debug(f'ML backend {self} is not ready to predict {task}')
            return
        if task.predictions.filter(model_version=self.model_version).exists():
            # prediction already exists
            logger.info(
                f'Skip creating prediction with ML backend {self} for task {task}: model version '
                f'{self.model_version} is up-to-date'
            )
            return
        ml_api = self.api

        task_ser = TaskSimpleSerializer(task).data
        ml_api_result = ml_api.make_predictions([task_ser], self.model_version, self.project)
        if ml_api_result.is_error:
            logger.info(f'Prediction not created for project {self}: {ml_api_result.error_message}')
            return
        results = ml_api_result.response['results']
        if len(results) == 0:
            logger.error(f'ML backend returned empty prediction for project {self.id}', extra={'sentry_skip': True})
            return
        prediction_response = results[0]
        task_id = task_ser['id']
        r = prediction_response['result']
        score = prediction_response.get('score')
        with conditional_atomic():
            prediction = Prediction.objects.create(
                result=r,
                score=safe_float(score),
                model_version=self.model_version,
                task_id=task_id,
                cluster=prediction_response.get('cluster'),
                neighbors=prediction_response.get('neighbors'),
                mislabeling=safe_float(prediction_response.get('mislabeling', 0)),
            )
            logger.debug(f'Prediction {prediction} created')

        return prediction

    def interactive_annotating(self, task, context=None, user=None):
        result = {}
        options = {}
        if user:
            options = {'user': user}
        if not self.is_interactive:
            result['errors'] = ["Model is not set to be used for interactive preannotations"]
            return result

        tasks_ser = InteractiveAnnotatingDataSerializer([task], many=True, expand=['drafts', 'predictions', 'annotations'], context=options).data
        ml_api_result = self.api.make_predictions(
            tasks=tasks_ser,
            model_version=self.model_version,
            project=self.project,
            context=context,
        )
        if ml_api_result.is_error:
            logger.info(f'Prediction not created for project {self}: {ml_api_result.error_message}')
            result['errors'] = [ml_api_result.error_message]
            return result

        if not (isinstance(ml_api_result.response, dict) and 'results' in ml_api_result.response):
            logger.info(f'ML backend returns an incorrect response, it must be a dict: {ml_api_result.response}')
            result['errors'] = ['Incorrect response from ML service: '
                                'ML backend returns an incorrect response, it must be a dict.']
            return result

        ml_results = ml_api_result.response.get(
            'results',
            [
                None,
            ],
        )
        if not isinstance(ml_results, list) or len(ml_results) < 1:
            logger.warning(f'ML backend has to return list with 1 annotation but it returned: {type(ml_results)}')
            result['errors'] = ['Incorrect response from ML service: '
                                'ML backend has to return list with more than 1 result.']
            return result

        result['data'] = ml_results[0]
        return result

    @staticmethod
    def get_versions_(url, project):
        api = MLApi(url=url)
        if not isinstance(project, Project):
            project = Project.objects.get(pk=project)
        return api.get_versions(project)

    def get_versions(self):
        return self.get_versions_(self.url, self.project)


class MLBackendPredictionJob(models.Model):

    job_id = models.CharField(max_length=128)
    ml_backend = models.ForeignKey(MLBackend, related_name='prediction_jobs', on_delete=models.CASCADE)
    model_version = models.TextField(
        _('model version'), blank=True, null=True, help_text='Model version this job is associated with'
    )
    batch_size = models.PositiveSmallIntegerField(
        _('batch size'), default=100, help_text='Number of tasks processed per batch'
    )

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)


class MLBackendTrainJob(models.Model):

    job_id = models.CharField(max_length=128)
    ml_backend = models.ForeignKey(MLBackend, related_name='train_jobs', on_delete=models.CASCADE)
    model_version = models.TextField(
        _('model version'),
        blank=True,
        null=True,
        help_text='Model version this job is associated with',
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def get_status(self):
        project = self.ml_backend.project
        ml_api = project.get_ml_api()
        if not ml_api:
            logger.error(f'Training job {self.id}: Can\'t collect training jobs for project {project.id}: ML API is null')
            return None
        ml_api_result = ml_api.get_train_job_status(self)
        if ml_api_result.is_error:
            if ml_api_result.status_code == 410:
                return {'job_status': 'removed'}
            logger.info(
                f'Training job {self.id}: Can\'t collect training jobs for project {project}: '
                f'ML API returns error {ml_api_result.error_message}'
            )
            return None
        return ml_api_result.response

    @property
    def is_running(self):
        status = self.get_status()
        return status['job_status'] in ('queued', 'started')


def _validate_ml_api_result(ml_api_result, tasks, curr_logger):
    if ml_api_result.is_error:
        curr_logger.info(ml_api_result.error_message)
        return False

    results = ml_api_result.response['results']
    if not isinstance(results, list) or len(results) != len(tasks):
        curr_logger.warning('Num input tasks is %d but ML API returns %d results', len(tasks), len(results))
        return False

    return True


@receiver(post_save, sender=MLBackend)
def create_ml_webhook(sender, instance, created, **kwargs):
    if not created:
        return
    ml_backend = instance
    webhook_url = ml_backend.url.rstrip('/') + '/webhook'
    project = ml_backend.project
    if Webhook.objects.filter(project=project, url=webhook_url).exists():
        logger.info(f'Webhook {webhook_url} already exists for project {project}: skip creating new one.')
        return
    logger.info(f'Create ML backend webhook {webhook_url}')
    ser = WebhookSerializer(data=dict(
        project=project.id,
        url=webhook_url,
        send_payload=True,
        send_for_all_actions=True)
    )
    if ser.is_valid():
        ser.save(organization=project.organization)
# class MLBackendQueue(models.Model):
#     """ Project Crawl Queue
#     """
#     project_id = models.IntegerField(_('project_id'), default=None, help_text='')
#     user_id = models.IntegerField(_('user_id'), default=None, help_text='')
#     ml_id = models.IntegerField(_('ml_id'), default=None, help_text='')
#     created_at = models.DateTimeField(_('created at'), auto_now_add=True)
#     updated_at = models.DateTimeField(_('updated at'), auto_now=True)
#     try_count = models.IntegerField(_('try_count'), default=5, help_text='')
#     max_tries = models.IntegerField(_('max_tries'), default=10, help_text='')
#     priority = models.IntegerField(_('priority'), default=0, help_text='')
#     status = models.TextField(_('status'), default="", help_text='')
#     epochs = models.IntegerField(_('epochs'), default=0, help_text='')
#     batch_size = models.IntegerField(_('batch_size'), default=0, help_text='')
#     def update_task(self):
#         update_fields = ['updated_at']

#         # updated_by
#         # request = get_current_request()
#         # if request:
#         #     # self.task.updated_by = request.user
#         #     update_fields.append('updated_by')

#         self.save(update_fields=update_fields)

#     def save(self, *args, **kwargs):
#         # "result" data can come in different forms - normalize them to JSON
#         # self.result = self.prepare_prediction_result(self.result, self.task.project)
#         # set updated_at field of task to now()
#         # self.update_task()
#         return super(MLBackendQueue, self).save(*args, **kwargs)

#     def delete(self, *args, **kwargs):
#         result = super().delete(*args, **kwargs)
#         # set updated_at field of task to now()
#         self.update_task()
#         return result
class MLGPU(models.Model):
    """ """
    ml_id = models.IntegerField(_('ml_id'), default=0)
    infrastructure_id = models.TextField(_('infrastructure_id'), default='')
    model_id = models.IntegerField(_("model_id"), default=0)
    model_history_rent_id = models.IntegerField(_("model_history_rent_id"), default=0, null=True)
    gpus_index = models.TextField(_('gpus_index'), default="0",help_text='GPU_0,GPU_1,...', null=True) 
    gpus_id = models.TextField(_('gpus_id'),help_text='1,2,3,4', null=True)  # if null -> using cpu
    compute_id = models.IntegerField(_('compute_id'),help_text='1', null=True) 
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)
    port = models.IntegerField(_('port'), null=True)
    class InstallStatus(models.TextChoices):
        FAILED = "failed", _("Failed")
        COMPLETED = "completed", _("Completed")
        INSTALLING = "installing", _("Installing")

    model_install = models.CharField(
        _("status"),
        max_length=64,
        choices=InstallStatus.choices,
        default=InstallStatus.INSTALLING,
        null=True,
    )
    def has_permission(self, user):
        return self.project.has_permission(user)

class MLBackendStatus(models.Model):
    ml_id = models.IntegerField(_('ml_id'), default=0)
    project_id = models.IntegerField(_('project_id'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)

    class Status(models.TextChoices):
        WORKER = 'worker', _('Worker')
        MASTER = 'master', _('Master')
        JOIN_MASTER = 'join_master', _('Join_master')
        REJECT_MASTER = 'reject_master', _('Reject_master')
        TRAINING = 'training', _('Training')
        STOP = 'stop', _('Stop')
        FINISH = 'finish', _('Finish')

    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.WORKER,
        null=True
    )

    status_training = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.JOIN_MASTER,
        null=True
    )

    class TypeTraining(models.TextChoices):
        MANUAL = "manual", _("Manual")
        AUTO = "auto", _("auto")

    type_training = models.CharField(
        _("type_training"),
        max_length=64,
        choices=TypeTraining.choices,
        default=TypeTraining.AUTO,
        null=True,
    )

class MLLogs(models.Model):
    ml_id = models.ForeignKey(MLBackend, on_delete=models.CASCADE, null=True)
    ml_gpu = models.ForeignKey(MLGPU, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    log_message = models.TextField(_('log message'), null=True)

    def has_permission(self, user):
        return self.project.has_permission(user)


class MLNetworkHistory(models.Model):
    ml_network = models.ForeignKey(MLNetwork, on_delete=models.CASCADE, related_name='history', verbose_name=_("ml_network"))
    ml_id = models.IntegerField(_("ml_id"), null=True)
    project_id = models.IntegerField(_("project_id"), null=True)
    model_id = models.IntegerField(_("model_id"), null=True)
    ml_gpu_id = models.IntegerField(_("model_id"), null=True)
    compute_gpu_id = models.IntegerField(_("compute_gpu_id"), null=True)
    checkpoint_id = models.IntegerField(_("checkpoint_id"), null=True)
    class Status(models.TextChoices):
        JOINED = 'joined', _('Joined')
        DISCONNECTED = 'disconnected', _('disconnected')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.JOINED,
        verbose_name=_("status")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)
