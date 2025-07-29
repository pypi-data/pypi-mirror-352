from model_marketplace.api import ModelTaskListCreateAPI, ModelTaskDetailAPI

from . import api, api_other
from . import checkpoint_api, dataset_api
from django.urls import include, path

app_name = 'model-marketplace'

_api_urlpatterns = [
    path(
        "<int:pk>/",
        api.ModelMarketplaceByIdAPI.as_view(),
        name="model-marketplace-by-id",
    ),
    path("<int:pk>", api.ModelMarketplaceDeleteAPI.as_view(), name="delete-id"),
    path("history-build-deploy/<int:pk>", api.BuildAndDeployDeleteAPI.as_view(), name="delete-history-build-deploy-id"),
    path("list-rent-model", api.HistoryRentModelListView.as_view(), name="rent-model"),
    path("list-build-model", api.HistoryBuildModelListView.as_view(), name="rent-model"),
    path("list-source-model", api.GetModelSourceProject.as_view(), name="rent-model"),
    path(
        "update/<int:pk>/",
        api.UpdateModelMarketplaceByIdAPI.as_view(),
        name="update-model-marketplace-by-id",
    ),
    path("", api.ModelMarketplaceAPI.as_view(), name="model-marketplace"),
    path(
        "list-sell",
        api.ModelMarketplaceBySellerAPI.as_view(),
        name="model-marketplace-seller-list",
    ),
    path(
        "catalog",
        api.CataLogModelMarketplaceAPI.as_view(),
        name="catalog-model-marketplace",
    ),
    path(
        "catalog/<int:pk>",
        api.CataLogModelMarketplaceDelAPI.as_view(),
        name="catalog-model-marketplace-del",
    ),
    path(
        "catalog-update/<int:pk>",
        api.CataLogModelMarketplaceUpdateAPI.as_view(),
        name="catalog-model-marketplace-update",
    ),
    path(
        "catalog-create",
        api.CataLogModelMarketplaceCreateAPI.as_view(),
        name="catalog-model-marketplace-create",
    ),
    path(
        "admin/catalog",
        api.CataLogModelMarketplacePaginateAPI.as_view(),
        name="catalog-model-marketplace-admin",
    ),
    path("buy/", api.ModelMarketplaceBuyAPI.as_view(), name="model-marketplace"),
    path(
        "like/<int:model_id>",
        api.ModelMarketplaceLikeAPI.as_view(),
        name="model-marketplace-like",
    ),
    path(
        "download/<int:model_id>",
        api.ModelMarketplaceDownloadAPI.as_view(),
        name="model-marketplace-download",
    ),
    path("add-model", api.AddModelApi.as_view(), name="add-model"),
    path(
        "commercialize-model",
        api.CommercializeModelApi.as_view(),
        name="commercialize-model",
    ),
    path("update-model/<int:pk>", api.AddModelApi.as_view(), name="update-model"),
    path("trade", api.AddModelApi.as_view(), name="trade"),
    path(
        "check-model-available/<int:model_id>",
        api.CheckModelAvailableAPI.as_view(),
        name="check-model-available",
    ),
    path(
        "install-model/<int:pk>/",
        api.InstallModelMarketplaceByIdAPI.as_view(),
        name="install-model-marketplace-by-id",
    ),
    path(
        "dowload-model-data/<int:pk>/",
        api.DownloadModelDataAPI.as_view(),
        name="dowload-model-data",
    ),
    path(
        "build-model-source/",
        api.BuildModelSourceAPI.as_view(),
        name="build-model-source",
    ),
    path(
        "deploy-model-source/",
        api.DeployModelAPI.as_view(),
        name="deploy-model-source",
    ),
    path(
        "calc-hf-model/",
        api.CalcHfModel.as_view(),
        name="calc-model-hf",
    ),
]
_api_urlpatterns_catalog = [
    path('', api.CatalogModelMarketplaceAPI.as_view(), name='catalog-model-marketplace'),
]
_api_urlpatterns_checkpoint = [
    path('', api.CheckpointModelMarketplaceAPI.as_view(), name='checkpoint-model-marketplace'),
    path('upload/<int:checkpoint_id>', checkpoint_api.ModelCheckpointUploadAPIView.as_view(), name='checkpoint-model-marketplace-upload'),
    path('download/<int:checkpoint_id>', checkpoint_api.ModelCheckpointDownloadAPIView.as_view(), name='checkpoint-model-marketplace-download'),
    path('<int:pk>', api.CheckpointModelMarketplaceUpdateAPI.as_view(), name='checkpoint-model-marketplace-update'),
    path('<int:pk>/', api.CheckpointModelMarketplaceDeleteAPI.as_view(), name='checkpoint-model-marketplace-delete'),
    path('upload/', checkpoint_api.ModelCheckpointUploadv2APIView.as_view(), name='upload-dataset'),
    path('upload-modelsource', checkpoint_api.UploadModelSourceAPI.as_view(), name='upload-model_source')
]

_api_urlpatterns_dataset = [
    path('', api.DatasetModelMarketplaceAPI.as_view(), name='dataset-model-marketplace'),
    path('<int:pk>', api.DatasetModelMarketplaceUpdateAPI.as_view(), name='dataset-model-marketplace-update'),
    path('<int:pk>/', api.DatasetModelMarketplaceDeleteAPI.as_view(), name='dataset-model-marketplace-delete'),
    path('upload/<int:dataset_id>', dataset_api.ModelDatasetUploadAPIView.as_view(), name='dataset-model-marketplace-upload'),
    path('download/<int:dataset_id>', dataset_api.ModelDatasetDownloadAPIView.as_view(), name='dataset-model-marketplace-download'),
]

urlpatterns = [
    path(
        "api/model_marketplace/",
        include((_api_urlpatterns, app_name), namespace="api model marketplace"),
    ),
    path(
        "api/catalog_model_marketplace/",
        include(
            (_api_urlpatterns_catalog, app_name),
            namespace="api catalog model marketplace",
        ),
    ),
    path(
        "api/checkpoint_model_marketplace/",
        include(
            (_api_urlpatterns_checkpoint, app_name),
            namespace="api checkpoint model marketplace",
        ),
    ),
    path(
        "api/dataset_model_marketplace/",
        include(
            (_api_urlpatterns_dataset, app_name),
            namespace="api dataset model marketplace",
        ),
    ),
    path("api/build-jupyter/", api_other.BuildJupyter.as_view(), name="build-jupyter"),
    path("api/model_marketplace_tasks/<int:marketplace_id>", api.ModelMarketplaceTasksAPI.as_view(), name="model-marketplace-tasks"),
    path('api/model_tasks/', ModelTaskListCreateAPI.as_view(), name='model-task-list-create'),
    path('api/model_tasks/<int:pk>/', ModelTaskDetailAPI.as_view(), name='model-task-detail'),
]
