from . import api, gpucard_api
from django.urls import include, path

app_name = 'compute-marketplace'

_api_urlpatterns = [
    path('', api.ComputeMarketplaceAPI.as_view(), name='compute-marketplace'),
    path('list', api.ComputeRentListAPIView.as_view(), name='compute-marketplace-list'),
    path('<int:pk>/', api.ComputeMarketplaceDetailAPIView.as_view(), name='compute-marketplace-detail'),
    path('<int:pk>', api.ComputeMarketplaceDeleteAPI.as_view(), name='compute-marketplace-delete'),
    path('list-supply', api.ComputeMarketplaceSupplierAPI.as_view(), name='compute-marketplace-supply'),
    path('list-rented', api.ComputeMarketplaceRentedAPI.as_view(), name='compute-marketplace-rented'),
    path('list-rented-card', api.ComputeMarketplaceRentedByCardAPI.as_view(), name='compute-marketplace-rented-card'),
    path('list-all-rented-compute', api.ListAllComputeMarketplaceRentedAPI.as_view(), name='compute-marketplace-rented-card'),
    path('list-rented-card/<int:pk>', api.HistoryRentComputeDeleteAPI.as_view(), name='history-rent-compute-delete'),
    path('catalog', api.CataLogComputeMarketplaceAPI.as_view(), name='catalog-compute-marketplace'),
    path('admin/catalog', api.CataLogComputePaginateAPI.as_view(), name='catalog-compute-marketplace-admin'),
    path('catalog/<int:pk>', api.CataLogComputeMarketplaceDelAPI.as_view(), name='catalog-compute-marketplace-del'),
    path('catalog-update/<int:pk>', api.CataLogComputeMarketplaceUpdateAPI.as_view(), name='catalog-compute-marketplace-update'),
    path('catalog-create', api.CataLogComputeMarketplaceCreateAPI.as_view(), name='catalog-compute-marketplace-create'),
    path('update/<int:pk>', api.ComputeMarketplaceUpdateAPI.as_view(), name='compute-marketplace-update'),
    path('rent/<int:pk>', api.ComputeMarketplaceRentAPI.as_view(), name='compute-marketplace-rent'),
    path('rent/', api.ComputeMarketplaceRentV2API.as_view(), name='compute-marketplace-rent-v2'),
    path('gpus/', api.ListGpu.as_view(), name='list-gpus'),
    path('user/token-worker/', api.ComputeMarketplaceGenTokenAPI.as_view(), name='compute-marketplace-gen-token'),
    path('user/secret-id', api.ComputeMarketplaceGenSecretAPI.as_view(), name='compute-marketplace-gen-secret'),
    path('user/create/', api.ComputeMarketplaceUserCreateAPI.as_view(), name='compute-marketplace-user-create'),
    path('user/create-full/', api.ComputeMarketplaceUserCreateFullAPI.as_view(), name='compute-marketplace-user-create-full'),
    path('gpu/update/<int:pk>', gpucard_api.UpdateComputeGpuApi.as_view(), name='update-compute-gpu-card'),
    path('gpu/rent', gpucard_api.RentComputeByGpuCardApi.as_view(), name='rent-compute-gpu-card'),
    path('gpu/list', gpucard_api.ListComputeGpuApi.as_view(), name='list-compute-gpu-card'),
    path('gpu/create', gpucard_api.CreateComputeGpuApi.as_view(), name='create-compute-gpu-card'),
    path('gpu/bulk-create/', gpucard_api.BulkCreateComputeGpuApi.as_view(), name='bulk_create_compute_gpu'),
    path('gpu-price/create', gpucard_api.ComputeGpuPriceCreateApi.as_view(), name='create-compute-gpu-price'),
    path('gpu-price/update', gpucard_api.ComputeGpuPriceUpdateApi.as_view(), name='update-compute-gpu-price'),
    path('gpu-price/bulk-create', gpucard_api.ComputeGpuPriceBulkCreateApi.as_view(), name='create-bulk-compute-gpu-price'),
    path('gpu-price/bulk-update', gpucard_api.ComputeGpuPriceBulkUpdateApi.as_view(), name='create-bulk-compute-gpu-price'),
    path('cpu-price/create', gpucard_api.ComputeCpuPriceApi.as_view(), name='create-compute-cpu-price'),
    path('cpu-price/', gpucard_api.ComputeGpuPriceRetrieveApi.as_view(), name='get-cpu-price'),
    path('time-working/create', api.ComputeTimeWorkingCreateAPI.as_view(), name='create-compute-time-working'),
    path('time-working/<int:compute_id>', api.ComputeTimeWorkingDetailAPI.as_view(), name='get-detail-compute-time-working'),
    path('time-working/<int:compute_id>/', api.ComputeTimeWorkingUpdateAPI.as_view(), name='compute-time-working-update'),
    path('by-ip/<str:ip_address>/', api.ComputeMarketplaceGetByIP.as_view(), name='compute-by-ip'),
    path('history-rent-computes', api.HistoryRentComputeAPI.as_view(), name='history-rent-computes'),
    path('computes-preference/<int:id>', api.ComputesPreferenceAPI.as_view(), name='computes-preference'),
    path('computes-preference-update/<int:id>', api.ComputesPreferenceUpdateAPI.as_view(), name='computes-preference-update'),
    path('auto-merge-card', api.AutoMergeCardAPI.as_view(), name='computes-preference-update'),
    path('recommend-price-card', gpucard_api.RecommendPriceAPI.as_view(), name='computes-preference-update'),
    path('compute-status-install/<int:id>', api.ComputeStatusInstalling.as_view(), name='computes-status-install'),
    path('compute-rented/<int:pk>/', api.ChangeServiceTypeComputeRented.as_view(), name='change-service-type-compute-rented'),
    path('download/<str:token_worker>/', api.DownloadFileView.as_view(), name='download-file'),
    path('create-compute-selfhost-wait-verify/', api.CreateComputeSelfhostWaitVerifyView.as_view(), name='create-compute-selfhost-wait-verify'),
    path('compute/selfhost/wait-verify/', api.CheckComputeSelfhostWaitVerifyView.as_view(), name='check_compute_selfhost_wait_verify'),
    path('compute/selfhost/process-self-host/', api.ProcessSelfHostAPI.as_view(), name='process_self_host'),

    path('compute/docker-status/', api.CheckComputeDockerStatus.as_view(), name='check-compute-docker-status'),
    path('compute/type-location', api.UpdateComputeTypeAndLocation.as_view(), name='update-compute-type-location'),
    path('dashboard/calculate', api.CalculateComputeModel.as_view(), name='calculate-compute'),
]

_api_compute_urlpatterns = [
    path('docker-kubernetes-status', api.ComputeDockerKubernetesAPI.as_view(), name='check-docker-kubernetes'),
    # path('gpu/create/', api.ComputeGPUCreateAPI.as_view(), name='compute_gpu_create'),
    # path('gpu/', api.ComputeGPUListAPI.as_view(), name='compute_gpu_list'),
    # path('gpu/<int:pk>/', api.ComputeGPURetrieveUpdateDestroyAPI.as_view(), name='compute_gpu_detail'),
    #  path('gpu/bulk-create/', api.ComputeGPUBulkCreateAPI.as_view(), name='compute_gpu_bulk_create'),
]

urlpatterns = [
    path('api/compute_marketplace/', include((_api_urlpatterns, app_name), namespace='api')),
    path('api/compute/', include((_api_compute_urlpatterns, app_name), namespace='api-compute')),
]
