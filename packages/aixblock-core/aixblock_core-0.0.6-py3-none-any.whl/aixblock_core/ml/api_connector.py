"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import logging
import os
import requests
import urllib
import attr
from django.contrib.auth.models import AnonymousUser

from django.db.models import Q, F, Count
from django.conf import settings
from requests.adapters import HTTPAdapter
# from core.version import get_git_version
from data_export.serializers import ExportDataSerializer
from aixblock_core.core.utils.params import get_env
from core.feature_flags import flag_set
from core.utils.common import load_func
from projects.models import Project
from model_marketplace.models import ModelMarketplace, CheckpointModelMarketplace, DatasetModelMarketplace
from compute_marketplace.models import ComputeMarketplace
from urllib.parse import urlparse, urlunparse

# version = get_git_version()
logger = logging.getLogger(__name__)

CONNECTION_TIMEOUT = float(get_env('ML_CONNECTION_TIMEOUT', 1))  # seconds
TIMEOUT_DEFAULT = float(get_env('ML_TIMEOUT_DEFAULT', 100))  # seconds

TIMEOUT_TRAIN = float(get_env('ML_TIMEOUT_TRAIN', 30))
TIMEOUT_PREDICT = float(get_env('ML_TIMEOUT_PREDICT', 100))
TIMEOUT_HEALTH = float(get_env('ML_TIMEOUT_HEALTH', 1))
TIMEOUT_SETUP = float(get_env('ML_TIMEOUT_SETUP', 3))
TIMEOUT_DUPLICATE_MODEL = float(get_env('ML_TIMEOUT_DUPLICATE_MODEL', 1))
TIMEOUT_DELETE = float(get_env('ML_TIMEOUT_DELETE', 1))
TIMEOUT_TRAIN_JOB_STATUS = float(get_env('ML_TIMEOUT_TRAIN_JOB_STATUS', 1))


class BaseHTTPAPI(object):
    MAX_RETRIES = 2
    HEADERS = {
        'User-Agent': 'aixblock/2.0.6',
    }

    def __init__(self, url, timeout=None, connection_timeout=None, max_retries=None, headers=None, **kwargs):
        self._url = url
        self._timeout = timeout or TIMEOUT_DEFAULT
        self._connection_timeout = connection_timeout or CONNECTION_TIMEOUT
        self._headers = headers or {}
        self._max_retries = max_retries or self.MAX_RETRIES
        self._sessions = {self._session_key(): self.create_session()}

    def create_session(self):
        session = requests.Session()
        session.headers.update(self.HEADERS)
        session.headers.update(self._headers)
        session.mount('http://', HTTPAdapter(max_retries=self._max_retries))
        session.mount('https://', HTTPAdapter(max_retries=self._max_retries))
        return session

    def _session_key(self):
        return os.getpid()

    @property
    def http(self):
        key = self._session_key()
        if key in self._sessions:
            return self._sessions[key]
        else:
            session = self.create_session()
            self._sessions[key] = session
            return session

    def _prepare_kwargs(self, kwargs):
        # add timeout if it's not presented
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self._connection_timeout, self._timeout

        # add connection timeout if it's not presented
        elif isinstance(kwargs['timeout'], float) or isinstance(kwargs['timeout'], int):
            kwargs['timeout'] = (self._connection_timeout, kwargs['timeout'])

    def request(self, method, *args, **kwargs):
        self._prepare_kwargs(kwargs)
        return self.http.request(method, *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)


@attr.s
class MLApiResult(object):
    url = attr.ib(default='')
    request = attr.ib(default='')
    response = attr.ib(default=attr.Factory(dict))
    headers = attr.ib(default=attr.Factory(dict))
    type = attr.ib(default='ok')
    status_code = attr.ib(default=200)

    @property
    def is_error(self):
        return self.type == 'error'

    @property
    def error_message(self):
        return self.response.get('error')


@attr.s
class MLApiScheme(object):
    tag_name = attr.ib()
    tag_type = attr.ib()
    source_name = attr.ib()
    source_type = attr.ib()
    source_value = attr.ib()

    def to_dict(self):
        return attr.asdict(self)


class MLApi(BaseHTTPAPI):

    def __init__(self, **kwargs):
        super(MLApi, self).__init__(**kwargs)
        self._validate_request_timeout = 10

    def _get_url(self, url_suffix):
        url = self._url
        if url[-1] != '/':
            url += '/'
        return urllib.parse.urljoin(url, url_suffix)

    def _request(self, url_suffix, request=None, verbose=True, method='POST', *args, **kwargs):
        assert method in ('POST', 'GET')
        url = self._get_url(url_suffix)
        request = request or {}
        compute_id = request.get("compute_id")
        if request:
            if compute_id is not None:
                compute = ComputeMarketplace.objects.filter(id=compute_id, deleted_at__isnull = True).first()
                if compute and compute.type == ComputeMarketplace.Type.PROVIDERVAST:
                    parsed_url = urlparse(url)
                    url = urlunparse(parsed_url._replace(path=""))  # remove url_suffix
                    method = "GET"
                if compute and compute.type != ComputeMarketplace.Type.PROVIDERVAST:
                    parsed_url = urlparse(url)
                    url = urlunparse(parsed_url._replace(path=""))  # remove url_suffix
                    method = "GET"
        headers = dict(self.http.headers)
        # if verbose:
        #     logger.info(f'Request to {url}: {json.dumps(request, indent=2)}')
        response = None
        try:
            if method == 'POST':
                response = self.post(
                    url=url, json=request, verify=False, *args, **kwargs
                )
            else:
                response = self.get(url=url,verify = False, *args, **kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Extending error details in case of failed request
            if flag_set('fix_back_dev_3351_ml_validation_error_extension_short', AnonymousUser):
                error_string = str(e) + (" " + str(response.text) if response else "")
            else:
                error_string = str(e)
            status_code = response.status_code if response is not None else 0
            return MLApiResult(url, request, {'error': error_string}, headers, 'error', status_code=status_code)
        status_code = response.status_code
        try:
            response = response.json()
        except ValueError as e:
            # logger.warning(f'Error parsing JSON response from {url}. Response: {response.content}', exc_info=True)
            return MLApiResult(
                url, request, {'error': str(e), 'response': response.content}, headers, 'error',
                status_code=status_code
            )
        # if verbose:
        #     logger.info(f'Response from {url}: {json.dumps(response, indent=2)}')

        return MLApiResult(url, request, response, headers, status_code=status_code)

    def _create_project_uid(self, project):

        time_id = int(project.created_at.timestamp())
        return f'{project.id}.{time_id}'

    def train(self, project, use_ground_truth=False, token = None, master_address = None, master_port = None, rank = None, world_size=None, workers=None, ps=None, configs = [], ml_backend_id=None):
        # TODO Replace AnonymousUser with real user from request
        user = AnonymousUser()
        channel_log = "training_logs"

        # Identify if feature flag is turned on
        if flag_set('ff_back_dev_1417_start_training_mlbackend_webhooks_250122_long', user):
            request = {
                'action': 'PROJECT_UPDATED',
                'project': load_func(settings.WEBHOOK_SERIALIZERS['project'])(instance=project).data
            }
            return self._request('webhook', request, verbose=False, timeout=TIMEOUT_PREDICT)
        else:
            # get only tasks with annotations
            tasks = project.tasks.annotate(num_annotations=Count('annotations')).filter(num_annotations__gt=0)
            from .models import MLBackend, MLGPU
            ml_backend = MLBackend.objects.filter(project_id = project.id, deleted_at__isnull=True).first()
            if ml_backend_id:
                channel_log = f'ml_logs_{ml_backend_id}'
                ml_gpu = MLGPU.objects.filter(ml_id = ml_backend_id).first()

            else:
                if ml_backend:
                    channel_log = f'ml_logs_{ml_backend.id}'
                ml_gpu = MLGPU.objects.filter(ml_id = ml_backend.id).first()
                
            checkpoint_id = None
            dataset_id = None
            checkpoint_version = None
            dataset_version = None
            push_hub_name = "aixblock"
            if ml_gpu:
                model_instance = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
                push_hub_name = model_instance.name.replace(" ", "_")
                if model_instance:
                    checkpoint_id = model_instance.checkpoint_storage_id
                    if checkpoint_id:
                        checkpoint_version = CheckpointModelMarketplace.objects.filter(id=checkpoint_id).first().version
                    dataset_id = model_instance.dataset_storage_id
                    if dataset_id:
                        dataset_version = DatasetModelMarketplace.objects.filter(id=dataset_id).first().version

            # create serialized tasks with annotations: {"data": {...}, "annotations": [{...}], "predictions": [{...}]}
            tasks_ser = ExportDataSerializer(tasks, many=True).data
            logger.debug(f'{len(tasks_ser)} tasks with annotations are sent to ML backend for training.')

            # if model_instance:
            #     config_param = json.loads(model_instance.config)
            # else:
            #     config_param = None
            
            # token_length = None
            # accuracy = None
            # mono = None
            # sampling_frequency = None
            # fps = None
            # resolution = None
            # image_width = None
            # image_height = None
            # framework = None
            # precision = None
            # calculate_compute_gpu = None
            # estimate_time = None
            # estimate_cost = None
            # TrainingArguments = None

            # try:
            #     token_length = config_param["token_length"] if config_param else '4096' 
            #     accuracy = config_param["accuracy"] if config_param else '70'
            #     mono = config_param["mono"] if config_param else True
            #     sampling_frequency = config_param["sampling_frequency"] if config_param else "48000"
            #     fps = config_param["fps"] if config_param else "60"
            #     resolution = config_param["resolution"] if config_param else "320"
            #     image_width = config_param["image_width"] if config_param else "256"
            #     image_height = config_param["image_height"] if config_param else "256"
            #     framework = config_param["framework"] if config_param else "pytorch"
            #     precision = config_param["precision"] if config_param else "fp16"
            #     calculate_compute_gpu = config_param["calculate_compute_gpu"] if config_param else '{"paramasters":759808,"mac":"2279424000000.0005","gpu_memory":16106127360,"tflops":4558848000000.001,"time":0.00019444444444444443,"total_cost":"0.159","total_power_consumption":0,"can_rent":true,"token_symbol":"usd"}'
            #     estimate_time = config_param["estimate_time"] if config_param else 1
            #     estimate_cost = config_param["estimate_cost"] if config_param else "0.159"
            #     TrainingArguments = config_param["TrainingArguments"] if config_param else {
            #                 "base_model": "meta-llama/Meta-Llama-3-8B-Instruct",
            #                 "model_type": "LlamaForCausalLM",
            #                 "tokenizer_type": "AutoTokenizer",
            #                 "load_in_8bit": True,
            #                 "load_in_4bit": False,
            #                 "strict": False,
            #                 "chat_template": "llama3",
            #                 "rl": "dpo",
            #             }
            # except:
            #     pass
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            push_to_hub = False
            push_to_hub_token = None

            if project.checkpoint_storage_huggingface and project.checkpoint_storage_huggingface != "":
                push_to_hub = True
                push_to_hub_token = project.checkpoint_storage_huggingface

            version = f'{date_str}-{time_str}'
            hf_model_id = f"{project.id}_{push_hub_name}_{version}_aixblock"
            request = {
                "annotations": tasks_ser,
                "command": "train",
                "project": self._create_project_uid(project),
                "label_config": project.label_config,
                "params": {
                    "login": project.task_data_login,
                    "password": project.task_data_password,
                    "project_id": project.id,
                    "dataset": dataset_id,
                    "dataset_version": dataset_version,
                    "checkpoint": checkpoint_id,
                    "checkpoint_version": checkpoint_version,
                    "rank": rank,
                    "host_name": f"{settings.ML_BACKEND_URL}",
                    "token": token,
                    "world_size": world_size,
                    "master_add": master_address,
                    "master_port": master_port,
                    "num_epochs": project.epochs,
                    "batch_size": project.batch_size,
                    "image_width": project.image_width,
                    "image_height": project.image_height,
                    "imgz": project.image_height,
                    "workers": workers,
                    "ps": ps,
                    "channel_log": channel_log,
                    "push_to_hub": push_to_hub,
                    "hf_model_id": hf_model_id,
                    "report_to": "tensorboard",
                    "push_to_hub_token": push_to_hub_token,
                    "configs": next(
                        (config for config in (configs or []) if config["type"] == "train"),
                        [],
                    ),
                }
            }

            if model_instance:
                # config_param = json.loads(model_instance.config)
                try:
                    try:
                        if isinstance(model_instance.config, dict):
                            config_str = json.dumps(model_instance.config)
                            config_param = json.loads(config_str)
                        else:
                            config_param = json.loads(model_instance.config)
                    except:
                        import ast
                        config_param = ast.literal_eval(model_instance.config)
                        # config_param = json.dumps(config_dict)
                    # Thêm từng key-value vào request["params"]
                    for key, value in config_param.items():
                        request["params"][key] = value
                except Exception as e:
                    # Xử lý lỗi nếu xảy ra
                    print(f"Error updating request params: {e}")

            return self._request('action', request, verbose=False, timeout=TIMEOUT_PREDICT)

    def stop_train(self, project, use_ground_truth=False, token=None):
        # TODO Replace AnonymousUser with real user from request
        user = AnonymousUser()
        # Identify if feature flag is turned on
        if flag_set(
            "ff_back_dev_1417_start_training_mlbackend_webhooks_250122_long", user
        ):
            request = {
                "action": "PROJECT_UPDATED",
                "project": load_func(settings.WEBHOOK_SERIALIZERS["project"])(
                    instance=project
                ).data,
            }
            return self._request(
                "webhook", request, verbose=False, timeout=TIMEOUT_PREDICT
            )
        else:
            # get only tasks with annotations
            tasks = project.tasks.annotate(num_annotations=Count("annotations")).filter(
                num_annotations__gt=0
            )
            from .models import MLBackend, MLGPU

            ml_backend = MLBackend.objects.filter(project_id=project.id).first()
            ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
            checkpoint_id = None
            dataset_id = None
            checkpoint_version = None
            dataset_version = None
            if ml_gpu:
                model_instance = ModelMarketplace.objects.filter(
                    id=ml_gpu.model_id
                ).first()
                checkpoint_id = model_instance.checkpoint_storage_id
                if checkpoint_id:
                    checkpoint_version = (
                        CheckpointModelMarketplace.objects.filter(id=checkpoint_id)
                        .first()
                        .version
                    )
                dataset_id = model_instance.dataset_storage_id
                if dataset_id:
                    dataset_version = (
                        DatasetModelMarketplace.objects.filter(id=dataset_id)
                        .first()
                        .version
                    )

            # create serialized tasks with annotations: {"data": {...}, "annotations": [{...}], "predictions": [{...}]}
            tasks_ser = ExportDataSerializer(tasks, many=True).data
            logger.debug(
                f"{len(tasks_ser)} tasks with annotations are sent to ML backend for training."
            )
            request = {
                "annotations": tasks_ser,
                "command": "stop",
                "project": self._create_project_uid(project),
                "label_config": project.label_config,
                "params": {
                    "login": project.task_data_login,
                    "password": project.task_data_password,
                    "project_id": project.id,
                    "dataset": dataset_id,
                    "dataset_version": dataset_version,
                    "checkpoint": checkpoint_id,
                    "checkpoint_version": checkpoint_version,
                    "token": token,
                    "num_epochs": project.epochs,
                    "batch_size": project.batch_size,
                    "image_width": project.image_width,
                    "image_height": project.image_height,
                },
            }
            return self._request(
                "action", request, verbose=False, timeout=TIMEOUT_PREDICT
            )

    def get_tensorboard(self, project, use_ground_truth=False, token=None):
        # TODO Replace AnonymousUser with real user from request
        user = AnonymousUser()
        # Identify if feature flag is turned on
        if flag_set(
            "ff_back_dev_1417_start_training_mlbackend_webhooks_250122_long", user
        ):
            request = {
                "action": "PROJECT_UPDATED",
                "project": load_func(settings.WEBHOOK_SERIALIZERS["project"])(
                    instance=project
                ).data,
            }
            return self._request(
                "webhook", request, verbose=False, timeout=TIMEOUT_PREDICT
            )
        else:
            # get only tasks with annotations
            tasks = project.tasks.annotate(num_annotations=Count("annotations")).filter(
                num_annotations__gt=0
            )
            from .models import MLBackend, MLGPU

            ml_backend = MLBackend.objects.filter(project_id=project.id).first()
            ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
            checkpoint_id = None
            dataset_id = None
            checkpoint_version = None
            dataset_version = None
            if ml_gpu:
                model_instance = ModelMarketplace.objects.filter(
                    id=ml_gpu.model_id
                ).first()
                checkpoint_id = model_instance.checkpoint_storage_id
                if checkpoint_id:
                    checkpoint_version = (
                        CheckpointModelMarketplace.objects.filter(id=checkpoint_id)
                        .first()
                        .version
                    )
                dataset_id = model_instance.dataset_storage_id
                if dataset_id:
                    dataset_version = (
                        DatasetModelMarketplace.objects.filter(id=dataset_id)
                        .first()
                        .version
                    )

            # create serialized tasks with annotations: {"data": {...}, "annotations": [{...}], "predictions": [{...}]}
            tasks_ser = ExportDataSerializer(tasks, many=True).data
            logger.debug(
                f"{len(tasks_ser)} tasks with annotations are sent to ML backend for training."
            )
            request = {
                "annotations": tasks_ser,
                "command": "tensorboard",
                "project": self._create_project_uid(project),
                "label_config": project.label_config,
                "params": {
                    "login": project.task_data_login,
                    "password": project.task_data_password,
                    "project_id": project.id,
                    "dataset": dataset_id,
                    "dataset_version": dataset_version,
                    "checkpoint": checkpoint_id,
                    "checkpoint_version": checkpoint_version,
                    "token": token,
                    "num_epochs": project.epochs,
                    "batch_size": project.batch_size,
                    "image_width": project.image_width,
                    "image_height": project.image_height,
                    "imgsz": project.image_height
                },
            }
            return self._request(
                "action", request, verbose=False, timeout=TIMEOUT_PREDICT
            )

    def get_dashboard(self, project, use_ground_truth=False, token=None):
        # TODO Replace AnonymousUser with real user from request
        user = AnonymousUser()
        # Identify if feature flag is turned on
        if flag_set(
            "ff_back_dev_1417_start_training_mlbackend_webhooks_250122_long", user
        ):
            request = {
                "action": "PROJECT_UPDATED",
                "project": load_func(settings.WEBHOOK_SERIALIZERS["project"])(
                    instance=project
                ).data,
            }
            return self._request(
                "webhook", request, verbose=False, timeout=TIMEOUT_PREDICT
            )
        else:
            # get only tasks with annotations
            tasks = project.tasks.annotate(num_annotations=Count("annotations")).filter(
                num_annotations__gt=0
            )
            from .models import MLBackend, MLGPU

            ml_backend = MLBackend.objects.filter(project_id=project.id).first()
            ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
            checkpoint_id = None
            dataset_id = None
            checkpoint_version = None
            dataset_version = None

            # create serialized tasks with annotations: {"data": {...}, "annotations": [{...}], "predictions": [{...}]}
            tasks_ser = ExportDataSerializer(tasks, many=True).data
            logger.debug(
                f"{len(tasks_ser)} tasks with annotations are sent to ML backend for training."
            )
            request = {
                "annotations": tasks_ser,
                "command": "dashboard",
                "project": self._create_project_uid(project),
                "label_config": project.label_config,
                "params": {
                    "login": project.task_data_login,
                    "password": project.task_data_password,
                    "project_id": project.id,
                    "dataset": dataset_id,
                    "dataset_version": dataset_version,
                    "checkpoint": checkpoint_id,
                    "checkpoint_version": checkpoint_version,
                    "token": token,
                    "num_epochs": project.epochs,
                    "batch_size": project.batch_size,
                    "image_width": project.image_width,
                    "image_height": project.image_height,
                    "imgsz": project.image_height
                },
            }
            return self._request(
                "action", request, verbose=False, timeout=TIMEOUT_PREDICT
            )

    def make_predictions(self, tasks, model_version, project, context=None):
        results = []
        HOSTNAME = settings.BASE_BACKEND_URL
        project_label_config = project.label_config

        for task in tasks:
            data = task['data']

            data_task = None

            if "image" in data:
                import re
                if "RectangleLabels" in project_label_config:
                    model_type = "rectanglelabels"
                else:
                    model_type = "polygonlabels"

                labels = re.findall(r'<Label value="(.*?)"', project_label_config)
                labels_str = ",".join(labels)


                request ={
                    "command": "predict",
                    "params": {
                        "prompt": labels_str,
                        "model_id": "facebook/opt-125m",
                        "token_lenght": 50,
                        "task": "text-generation",
                        "model_type": model_type,
                        "text": None,
                        "voice": None
                    },
                    "project": f'{project.id}'
                }
                import base64
                image = data["image"]
                if "/data/upload" in image:
                    image_data = f"{HOSTNAME}{image}"
                else:
                    image_data = image
                
                try:
                    response = requests.get(image_data)
                    image_base64 = base64.b64encode(response.content).decode('utf-8')
                    request["params"]["image"] = image_base64
                except:
                    request["params"]["image"] = ""

            elif "video" in data:
                request = {
                    "command": "predict",
                    "params": {
                        "prompt": "car,Man,Woman,Other",
                        "model_id": "facebook/opt-125m",
                        "token_lenght": 50,
                        "task": "text-generation",
                        "text": "",
                        "video_frame": 3,
                        "video_time": 0,
                        # "video_total_frame": 638,
                        "confidence_threshold": 0.01,
                        "iou_threshold": 0.01,
                        "frame": 2,
                        "full_video": True,
                        "task_id": 937
                    },
                    "project": "229"
                }

                def get_frame_count(video_url):
                    import cv2
                    # Tải video từ URL về và chuyển thành đối tượng OpenCV
                    cap = cv2.VideoCapture(video_url)
                    if not cap.isOpened():
                        print("Cannot open video.")
                        return None
                    
                    # Lấy số lượng frame từ video
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    cap.release()
                    
                    return frame_count
                
                video = data["video"]
                if "/data/upload" in video:
                    video_url = f"{HOSTNAME}{video}"
                else:
                    video_url = video
                
                frame_count = get_frame_count(video_url)
                request["params"]["video_url"] = video_url
                request["params"]["video_total_frame"] = frame_count

            elif "pcd" in data:
                pcd = data["pcd"]
                if "/data/upload" in pcd:
                    data_task = f"{HOSTNAME}{pcd}"
                else:
                    data_task = pcd

            elif "audio" in data:
                audio = data["audio"]
                if "/data/upload" in audio:
                    data_task = f"{HOSTNAME}{audio}"
                else:
                    data_task = audio

            elif "text" in data:
                text = data["text"]
                prompt = ""
                model_id = "facebook/opt-125m"
                if "Text Summarization" in project.label_config_title:
                    task_name = "text-generation"
                elif "Named Entity Recognition" in project.label_config_title:
                    task_name = "ner"
                    model_id = "SKT27182/Name_Entity_Recognizer"
                elif "Question Answering" in project.label_config_title:
                    task_name = "question-answering"
                    prompt = data["question"]
                elif "Machine Translation" in project.label_config_title:
                    task_name = "translation"
                else:
                    task_name = "text-generation"

                request = {
                    "command": "predict",
                    "params": {
                        "prompt": prompt,
                        "model_id": model_id,
                        "token_lenght": project.llm_token if project.llm_token else 50,
                        "task": task_name,
                        "text": text,
                        "max_gen_len": 1024,
                        "temperature": 0.9,
                        "top_p": 0.5,
                        "seed": 0,
                        "task_id": task['id']
                    },
                    "project": f'{project.id}'
                }

            res = self._request('action', request, verbose=False, timeout=TIMEOUT_PREDICT)

            if 'results' in res.response:
                results.append(res.response['results'])

        return results

    # def health(self):
    #     return self._request('health', method='GET', timeout=TIMEOUT_HEALTH)

    def validate(self, config):
        return self._request('validate', request={'config': config}, timeout=self._validate_request_timeout)

    def setup(self, project, model_version=None, compute_id = None):
        # print(project)
        # print(self._create_project_uid(project))
        from ml.models import MLBackend
        ml_backend = MLBackend.objects.filter(
            project=int(float(self._create_project_uid(project))),
            deleted_at__isnull=True
        )
        # print(ml_backend.first())
        ml_id = 0
        if len(ml_backend)>0 :
            ml = ml_backend.first()
            ml_id = ml.id
        return self._request(
            "setup",
            request={
                "compute_id": compute_id,
                "ml_id": ml_id,
                "project": self._create_project_uid(project),
                "schema": project.label_config,
                "hostname": (
                    settings.HOSTNAME
                    if settings.HOSTNAME
                    else ("http://localhost:" + str(settings.INTERNAL_PORT))
                ),
                "access_token": project.created_by.auth_token.key,
                "model_version": model_version,
            },
            timeout=TIMEOUT_SETUP,
        )

    def duplicate_model(self, project_src, project_dst):
        return self._request('duplicate_model', request={
            'project_src': self._create_project_uid(project_src),
            'project_dst': self._create_project_uid(project_dst)
        }, timeout=TIMEOUT_DUPLICATE_MODEL)

    def delete(self, project):
        return self._request('delete', request={'project': self._create_project_uid(project)}, timeout=TIMEOUT_DELETE)

    def get_train_job_status(self, train_job):
        return self._request('job_status', request={'job': train_job.job_id}, timeout=TIMEOUT_TRAIN_JOB_STATUS)

    def get_versions(self, project):
        return self._request('versions', request={
            'project': self._create_project_uid(project)
        }, timeout=TIMEOUT_SETUP, method='POST')


def get_ml_api(project):
    if project.ml_backend_active_connection is None:
        return None
    if project.ml_backend_active_connection.ml_backend is None:
        return None
    return MLApi(
        url=project.ml_backend_active_connection.ml_backend.url,
        timeout=project.ml_backend_active_connection.ml_backend.timeout
    )
