from compute_marketplace.serializers import TradeResourceSerializer
from compute_marketplace.models import Trade, Portfolio
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from .models import ModelMarketplace #, ModelPrice
from django.utils import timezone
from datetime import timedelta
import os
import zipfile
import time
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import ZipFileUploadSerializer
from jenkinsapi.jenkins import Jenkins
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
import requests
import base64
from core.settings.base import JENKINS_URL

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Trade/Rent Compute Gpu',
))
class BuyModelApi(generics.CreateAPIView):
    serializer_class = TradeResourceSerializer
    queryset = Trade.objects.all()

    def post(self, request, *args, **kwargs):
        model_id = self.request.data.get('resource_id')
        model_trade = Trade.objects.filter(resource_id=model_id, status='renting').first()
        if model_trade:
            return Response({'error': 'ModelMarketplace is rented'}, status=400)
        user_id = self.request.user.id
        token_symbol = self.request.data.get('token_symbol')
        portfolio = Portfolio.objects.filter(account_id=user_id, token_symbol=token_symbol).first()
        if not portfolio:
            return Response({'error': 'Portfolio not found'}, status=404)

        # update status of compute gpu
        model = ModelMarketplace.objects.filter(id=model_id).first()
        model.status = "renting"
        # modelPrice = ModelPrice.objects.filter(model_id=model_id, token_symbol=token_symbol).first()
        # if modelPrice:
        #     price = modelPrice.price
        #     amount = price
        #     if (timezone.now() - model.created_at) < timedelta(days=30):
        #         amount = price * 0.9
        #     portfolio.amount_holding = portfolio.amount_holding - amount
        #     portfolio.save()
        #     serializer = self.get_serializer(data=request.data)
        #     serializer.is_valid(raise_exception=False)
        #     serializer.validated_data['price'] = price
        #     serializer.validated_data['amount'] = price
        #     serializer.validated_data['account_id'] = user_id
        #     serializer.validated_data['resource'] = 'model'
        #     self.perform_create(serializer)
        #     model.save()
        #     return Response(serializer.data, status=201)

        # else:
        #     return Response({'error': 'ModelPrice not found'}, status=404)


def normalize_name(name):
    return name.lower().replace(" ", "-")


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Model Marketplace"],
        operation_summary="Upload and build project on Jenkins server",
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                description="ZIP file containing the project source code",
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="name",
                in_=openapi.IN_FORM,
                description="Optional name for the project. If not provided, the name will be derived from the ZIP file name.",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        consumes=["multipart/form-data"],
    ),
) 
class BuildJupyter(generics.CreateAPIView):
    parser_classes = [MultiPartParser]  # Set the appropriate parser for file uploads

    def post(self, request, *args, **kwargs):
        from core.settings.base import JENKINS_TOKEN

        # Access file and name directly from request
        zip_file = request.FILES.get("file")
        name = request.data.get("name")

        if not zip_file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Normalize the project name
        model_name = normalize_name(name) if name else Path(zip_file.name).stem

        # Jenkins configuration
        jenkins_url = JENKINS_URL
        jenkins = Jenkins(jenkins_url, username="admin", password="admin123@")

        job_name = model_name

        # Path to Jenkins job config XML file
        job_config_path = os.path.join(os.path.dirname(__file__), "jenkins-no-git.xml")
        with open(job_config_path, "r") as file:
            xml = file.read()

        # Create or update the Jenkins job
        if job_name not in jenkins.jobs:
            jenkins.create_job(jobname=job_name, xml=xml)
        else:
            job = jenkins[job_name]
            # job.update_config(xml)

        # Trigger the Jenkins build
        job = jenkins[job_name]
        try:
            if job.is_queued_or_running():
                return Response(
                    {"message": "A build is already running for this job."},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                encoded_file = base64.b64encode(zip_file.read()).decode('utf-8')

                files = {
                    'THEFILE': (zip_file.name, encoded_file, 'application/zip')
                }

                response = requests.post(
                    f"{jenkins_url}/job/{job_name}/buildWithParameters",
                    auth=("admin", JENKINS_TOKEN),
                    files=files,
                    data={"THEFILE": zip_file.name},
                )
                response.raise_for_status()
                time.sleep(20)
                # Wait for the build to complete using Jenkins API
                build_number = job.get_next_build_number()
                build = job.get_build(build_number)
                build.block_until_complete()

                # Check number of builds
                current_number = job.get_next_build_number()
                complete_last_build = job.get_last_completed_build()
                if complete_last_build.buildno == current_number and current_number> 1:
                    print(f"Deleting job {job_name} after build completion.")
                    jenkins.delete_job(job_name)
                    print(f"Job {job_name} deleted.")
                return Response(
                    {"message": "Build triggered and job handled successfully."},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
