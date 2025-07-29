from rest_framework import generics
from .models import User_Point
from .serializers import UserPointSerializer
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from core.permissions import ViewClassPermission, all_permissions
from core.utils.paginate import SetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
import drf_yasg.openapi as openapi
from django.db.models import Q

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Get Point of User',
        operation_description="Get Point of User",
        manual_parameters=[openapi.Parameter('email', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Email user', required=True)]
    ),
)

@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Reward Point'],
        operation_summary='Update point of User',
        operation_description="Update point of User",
    ),
)

class UserPointAPI(generics.ListCreateAPIView):
    serializer_class = UserPointSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.reward_point_view,
        POST=all_permissions.reward_point_create,
    )
    # pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]

    def post(self, request, *args, **kwargs):
        user = request.user
        point = request.data.get('point')
        if not User_Point.objects.filter(user=user).exists():
            User_Point.objects.create(
                user=user,
                point=point
            )
        else:
            user_point = User_Point.objects.get(user=user)
            user_point.point = point
            user_point.save()

        return super(UserPointAPI, self).post(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        email = self.request.query_params.get('email').lower()
        queryset = User_Point.objects.filter(Q(user=user) | Q(user__email=email))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset.first(), many=False)
        return Response(serializer.data)