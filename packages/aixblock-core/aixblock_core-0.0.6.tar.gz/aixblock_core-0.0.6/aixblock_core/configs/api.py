from rest_framework import generics
from rest_framework import status
from .models import InstallationService
from .serializers import (
    InstallationServiceSerializer,
    InstallationServiceAfterDeploySerializer,
)
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from core.permissions import ViewClassPermission, all_permissions
from core.utils.paginate import SetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from core.settings.base import JENKINS_KEY


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Config Server"],
        operation_summary="Get Service Install",
        operation_description="Get Service Install",
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Config Server"],
        operation_summary="Create Service install",
        operation_description="Create Service install",
        request_body=InstallationServiceSerializer,
    ),
)
class InstallationServiceListAPI(generics.ListCreateAPIView):
    serializer_class = InstallationServiceSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.installation_service_view,
        POST=all_permissions.installation_service_create,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(InstallationServiceListAPI, self).post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = InstallationService.objects.all()
        return queryset


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        tags=["Config Server"],
        operation_summary="Update an Installation Service",
        operation_description="Update an existing Installation Service",
        request_body=InstallationServiceSerializer,
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Config Server"],
        operation_summary="Update an Installation Service",
        operation_description="Update an existing Installation Service",
        request_body=InstallationServiceSerializer,
    ),
)
class InstallationServiceUpdateAPI(generics.UpdateAPIView):
    serializer_class = InstallationServiceSerializer
    queryset = InstallationService.objects.all()
    permission_required = ViewClassPermission(
        PUT=all_permissions.installation_service_change,
    )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["Config Server"],
        operation_summary="Delete an Installation Service",
        operation_description="Delete an Installation Service",
    ),
)
class InstallationServiceDeleteAPI(generics.DestroyAPIView):
    permission_required = ViewClassPermission(
        DELETE=all_permissions.installation_service_delete,
    )

    def get_queryset(self):
        return InstallationService.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        data = {"success": True, "status_code": 200, "msg": "Successfully Deleted"}

        return Response(data, status=status.HTTP_200_OK)

    def get_object(self):
        action_point_id = self.kwargs.get("pk")
        action_point = get_object_or_404(InstallationService, pk=action_point_id)
        return action_point


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Config Server"],
        operation_summary="Update an Installation Service Version after deploy new version",
        operation_description="Update an existing Installation Service  Version after deploy new version",
        request_body=InstallationServiceAfterDeploySerializer,
    ),
)
class InstallationServiceUpdateAfterDeployAPI(generics.UpdateAPIView):
    serializer_class = InstallationServiceAfterDeploySerializer
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission
    def patch(self, request, *args, **kwargs):

        key = request.data.get("key", "")
        image = request.data.get("image", "")
        version = request.data.get("version", "")
        environment = request.data.get("environment", "")
        # verification key with jenkins
        if key != JENKINS_KEY:
            return Response({"message": "Invalid key"}, status=403)
        installation_service = InstallationService.objects.filter(image=image, environment=environment).first()
        if installation_service is  None:
            installation_service = InstallationService.objects.create(
                image=image,
                environment=environment,
                version=version,
                name="AiXblock Platform",
                registry="hub.docker.com",
                status="active"
            )
            installation_service.save()
            return Response(
                {
                    "message": "Created new InstallationService",
                },
                status=201,
            )
        installation_service.version = version
        installation_service.save()

        return Response(data=True, status=200)
