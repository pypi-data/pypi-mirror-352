from comments import api
from django.urls import include, path

app_name = 'comments'

_api_urlpatterns = [
    path('', api.CommentAPI.as_view(), name='comments'),
    path('<int:pk>/', api.CommentResolveAPI.as_view(), name='comment-resolve'),
]

urlpatterns = [
    path('api/comments/', include((_api_urlpatterns, app_name), namespace='api')),
]
