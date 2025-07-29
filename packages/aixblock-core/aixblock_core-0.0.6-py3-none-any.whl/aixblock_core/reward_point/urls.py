from django.urls import path, include
from . import api, userpoint_api

app_name = 'reward_point'

_api_urlpatterns = [
    path('', api.ActionPointListAPI.as_view(), name='action-point-list'),
    path('<int:pk>', api.ActionPointUpdateAPI.as_view(), name='action-point-update'),
    path('<int:pk>/', api.ActionPointDeleteAPI.as_view(), name='action-point-delete'),
]

_api_userpoint_urlpatterns = [
    path('user_action_history/', api.UserActionHistoryAPI.as_view(), name='action-point-list'),
    path('user_point', userpoint_api.UserPointAPI.as_view(), name='user-point'),
]

urlpatterns = [
    path('api/reward_point/', include((_api_urlpatterns, app_name), namespace='api-action-point')),
    path('api/reward_point/user/', include((_api_userpoint_urlpatterns, app_name), namespace='api-user-point')),
    path('api/reward_point/rank_point', api.RankPointListAPI.as_view(), name='rank-point-list')
]
