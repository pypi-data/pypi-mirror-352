from rest_framework import generics
from rest_framework import status
from users.models import Rank_Point
from .models import Action_Point, User_Action_History, User_Point
from users.serializers import RankPointSerializer
from .serializers import ActionPointSerializer, ActionPointFilter, UserActionHistorySerializer, UserActionHistoryFilter
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from core.permissions import ViewClassPermission, all_permissions
from core.utils.paginate import SetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Get Actions Point',
        operation_description="Get List Action Point",
    ),
)

@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Create a action point',
        operation_description="Create a action point",
    ),
)

class ActionPointListAPI(generics.ListCreateAPIView):
    serializer_class = ActionPointSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.reward_point_view,
        POST=all_permissions.reward_point_create,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActionPointFilter
    
    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(ActionPointListAPI, self).post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Action_Point.objects.all()
        search_param = self.request.query_params.get('search')
        if search_param:
            queryset = self.filter_queryset(queryset)
        return queryset

@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Update an action point',
        operation_description="Update an existing action point",
    ),
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Update an action point',
        operation_description="Update an existing action point",
    ),
)
class ActionPointUpdateAPI(generics.UpdateAPIView):
    serializer_class = ActionPointSerializer
    queryset = Action_Point.objects.all()
    permission_required = ViewClassPermission(
        PUT=all_permissions.reward_point_change,
    )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

@method_decorator(
    name='delete',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Delete an action point',
        operation_description="Delete an existing action point",
    ),
)

class ActionPointDeleteAPI(generics.DestroyAPIView):
    permission_required = ViewClassPermission(
        DELETE=all_permissions.reward_point_delete,
    )

    def get_queryset(self):
        return Action_Point.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        data = {
            "success": True,
            "status_code": 200,
            "msg": "Successfully Deleted"
        }

        return Response(data, status=status.HTTP_200_OK)

    def get_object(self):
        action_point_id = self.kwargs.get('pk')
        action_point = get_object_or_404(Action_Point, pk=action_point_id)
        return action_point
    

## History User Action
@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Get User Action History',
        operation_description="Get List Action History",
    ),
)

@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Create action history for user',
        operation_description="Create action history for user",
    ),
)

class UserActionHistoryAPI(generics.ListCreateAPIView):
    serializer_class = UserActionHistorySerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.reward_point_view,
        POST=all_permissions.reward_point_create,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserActionHistoryFilter
    
    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        point = request.data.get('point')
        status_point = request.data.get('status')
        
        # Create User_Action_History first
        user_action_history_serializer = self.get_serializer(data=request.data)
        if user_action_history_serializer.is_valid():
            user_action_history_serializer.save()
        else:
            return super(UserActionHistoryAPI, self).post(request, *args, **kwargs)

        # Then create or update User_Point
        if not User_Point.objects.filter(user_id=user_id).exists():
            if status_point == 0:
                User_Point.objects.create(
                    user_id=user_id,
                    point=point
                )
        else:
            user_point = User_Point.objects.get(user_id=user_id)
            if status_point == 0:
                user_point.point += point
            else:
                user_point.point = max(0, user_point.point - point)

            user_point.save()

        return super(UserActionHistoryAPI, self).post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User_Action_History.objects.filter(user_id = self.request.user.id).order_by('-id')
        return queryset 
    
@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Get all rank_point',
        operation_description="Get List Rank",
    ),
)

@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Get all rank_point',
        operation_description="Get List Rank",
    ),
)

class RankPointListAPI(generics.ListCreateAPIView):
    serializer_class = RankPointSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.reward_point_view,
        POST=all_permissions.reward_point_create,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save()
    
    def get_queryset(self):
        queryset = Rank_Point.objects.all().order_by('-minimum_points')
        return queryset 