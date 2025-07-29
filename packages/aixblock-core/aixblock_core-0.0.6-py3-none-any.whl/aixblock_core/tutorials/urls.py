from django.urls import path, include

from . import api

app_name = 'tutorials'

# _api_urlpatterns_tutorial = [
#     path('list', api.TutorialListApi.as_view(), name='tutorials-list'),
# ]

# _api_urlpatterns_group = [
#     path('list', api.TutorialGroupListApi.as_view(), name='tutorial-group-list'),
#     path('create', api.TutorialGroupCreateApi.as_view(), name='tutorial-group-create'),
#     path('update/<int:pk>', api.TutorialGroupUpdateApi.as_view(), name='tutorial-group-update'),
#     path('delete/<int:pk>', api.TutorialGroupDeleteApi.as_view(), name='tutorial-group-delete'),
# ]

# _api_urlpatterns_subgroup = [
#     path('list', api.TutorialSubgroupListApi.as_view(), name='tutorial-sub-group-list'),
#     path('create', api.TutorialSubgroupCreateApi.as_view(), name='tutorial-sub-group-create'),
#     path('update/<int:pk>', api.TutorialSubgroupUpdateApi.as_view(), name='tutorial-sub-group-update'),
#     path('delete/<int:pk>', api.TutorialSubgroupDeleteApi.as_view(), name='tutorial-sub-group-delete'),
# ]

# _api_urlpatterns_section = [
#     path('list', api.TutorialSectionContentListApi.as_view(), name='tutorial-section-content-list'),
#     path('create', api.TutorialSectionContentCreateApi.as_view(), name='tutorial-section-content-create'),
#     path('update/<int:pk>', api.TutorialSectionContentUpdateApi.as_view(), name='tutorial-section-content-update'),
#     path('delete/<int:pk>', api.TutorialSectionContentDeleteApi.as_view(), name='tutorial-section-content-delete'),
# ]

# _api_urlpatterns_content = [
#     path('create', api.TutorialContentCreateApi.as_view(), name='tutorial-content-create'),
#     path('update/<int:pk>', api.TutorialContentUpdateApi.as_view(), name='tutorial-content-update'),
#     path('delete/<int:pk>', api.TutorialContentDeleteApi.as_view(), name='tutorial-content-delete'),
# ]

_api_urlpatterns_documents = [
    path('pages', api.DocumentPagesListGetApi.as_view(), name='document-get-workspace'),
    path('page/<str:id>', api.DocumentPageGetApi.as_view(), name='document-get-page')
]

urlpatterns = [
    # path('api/tutorials/', include((_api_urlpatterns_tutorial, app_name), namespace='api')),
    # path('api/tutorials/group/', include((_api_urlpatterns_group, app_name), namespace='group-api')),
    # path('api/tutorials/subgroup/', include((_api_urlpatterns_subgroup, app_name), namespace='subgroup-api')),
    # path('api/tutorials/section/', include((_api_urlpatterns_section, app_name), namespace='section-api')),
    # path('api/tutorials/content/', include((_api_urlpatterns_content, app_name), namespace='content-api')),
    path('api/documents/', include((_api_urlpatterns_documents, app_name), namespace='document-api'))
    
]
