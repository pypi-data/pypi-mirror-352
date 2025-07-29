from . import api
from django.urls import include, path

app_name = 'annotation-template'

_api_urlpatterns = [
    path("", api.AnnotationTemplateAPI.as_view(), name="annotation-template"),
    path(
        "list",
        api.CatalogAnnotationTemplateListAPI.as_view(),
        name="annotation-template-list",
    ),
    path(
        "update/<int:pk>",
        api.AnnotationTemplateUpdateAPI.as_view(),
        name="annotation-template-update",
    ),
    path(
        "delete/<int:pk>",
        api.AnnotationTemplateDelAPI.as_view(),
        name="annotation-template-delete",
    ),
    path("import-template/", api.TemplateListAPI.as_view(), name="import-template"),
    path(
        "annotation-template/<int:pk>/",
        api.AnnotationTemplateDetailAPIView.as_view(),
        name="annotation-template-detail",
    ),
]
_api_urlpatterns_catalog = [
    path('', api.CatalogAnnotationTemplateAPI.as_view(), name='catalog-annotation-template'),
]

urlpatterns = [
    path('api/annotation_template/', include((_api_urlpatterns, app_name), namespace='api annotation template')),
    path('api/catalog_annotation_template/', include((_api_urlpatterns_catalog, app_name), namespace='api catalog annotation template')),
]
