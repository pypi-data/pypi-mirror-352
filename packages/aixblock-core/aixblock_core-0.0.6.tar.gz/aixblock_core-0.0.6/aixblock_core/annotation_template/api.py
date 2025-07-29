from .models import AnnotationTemplate
from .serializers import (
    AnnotationTemplateserializer,
    AnnotationDetailTemplateserializer,
)
from core.permissions import ViewClassPermission, all_permissions
from rest_framework import generics
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
import drf_yasg.openapi as openapi
import pathlib
from core.utils.io import find_dir, find_file, read_yaml
from django.conf import settings
from model_marketplace.models import ModelMarketplace, CatalogModelMarketplace
from core.utils.paginate import SetPagination
from .functions import import_annotation_templates
from django.shortcuts import get_object_or_404

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Get Annotation Template',
        operation_description="""
        Get task data, metadata, annotations and other attributes for a specific labeling task by task ID.
        """,
        manual_parameters=[
            # openapi.Parameter(
            #     name='ordering',
            #     type=openapi.TYPE_STRING,
            #     in_=openapi.IN_PATH,
            #     description='Annotation Template ID'
            # ),
        ]))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Update Annotation Template',
        operation_description='Update the attributes of an existing labeling task.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Annotation Template ID'
            ),
        ],
        request_body= AnnotationTemplateserializer))
@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Delete Annotation Template',
        operation_description='Delete a task in AiXBlock. This action cannot be undone!',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Annotation Template ID'
            ),
        ],
        ))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Post Annotation Template',
    operation_description='Perform an action with the selected items from a specific view.',
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Post Annotation Template',
    operation_description='Perform an action with the selected items from a specific view.',
))
class AnnotationTemplateAPI(generics.ListCreateAPIView):
    serializer_class = AnnotationTemplateserializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get_queryset(self):
        # Annotation_pk = self.request.query_params.get('Annotation')
        # annotation_pk = self.request.query_params.get('annotation')
        # ordering = self.request.query_params.get('ordering')
        return AnnotationTemplate.objects.order_by('-id')

    def get(self, request, *args, **kwargs):

        import json
        # from django.core import serializers
        # from django.http import HttpResponse        
        import datetime
        import json
        import os

        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime)):
                return o.isoformat()
        obj = list( AnnotationTemplate.objects.filter(is_deleted=False).order_by('-id').values() )
        
       
        # print(obj)
        # qs_json = serializers.serialize('json', obj)
        # return HttpResponse(obj, content_type='application/json')
        # results = AnnotationTemplate.objects.raw('SELECT group FROM annotation_template GROUP BY group')
        if settings.DJANGO_DB == "sqlite":
            results = AnnotationTemplate.objects.filter(is_deleted=False).values('group').distinct()
        else:
            results = AnnotationTemplate.objects.filter(is_deleted=False).order_by('group').distinct('id', 'group').values('group')
        # except:
        # print(results)
        groups = []
        for f in results:
        #    print(f.group)
           if groups.count(f["group"]) == 0:
                groups.append(f["group"])
        print(groups)
        return Response({"templates":json.loads(json.dumps(
        obj,
        sort_keys=True,
        indent=1,
        default=default
        )),"groups":json.loads(json.dumps( groups))
#           [
#     "Computer Vision",
#     "Segments Anythings",
#     "Yolov8",
#     "3D Model",
#     "Detectron2",
#     "Natural Language Processing",
#     "Audio/Speech Processing",
#     "Conversational AI",
#     "Ranking & Scoring",
#     "Structured Data Parsing",
#     "Time Series Analysis",
#     "Videos",
#     "Huggingface NLP",
#     "Huggingface Computer Vision",
#     "Generative AI",
#     "Large Language Model"
#   ]
  })
        # return super(AnnotationTemplateAPI, self).get(request, *args, **kwargs)

    def perform_create(self, serializer):
        # serializer.save(created_by=self.request.user)
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).delete(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).patch(request, *args, **kwargs)

    # @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).put(request, *args, **kwargs)


class AnnotationTemplateResolveAPI(generics.UpdateAPIView):
    permission_required = ViewClassPermission(
        PATCH=all_permissions.annotations_view,
    )

    def get_queryset(self):
        # AnnotationTemplate_pk = self.request.data.get('id')
        # Annotation_pk = self.request.query_params.get('Annotation')
        return AnnotationTemplate.objects#.filter( id=AnnotationTemplate_pk)

    def patch(self, request, *args, **kwargs):
        AnnotationTemplate = self.get_object()

        if AnnotationTemplate is not None:
            # AnnotationTemplate.is_resolved = request.data.get('is_resolved')
            # AnnotationTemplate.save(update_fields=frozenset(['is_resolved']))
            return Response(AnnotationTemplateserializer(AnnotationTemplate).data)

        return Response(status=404)
@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Get Annotation Template by id',
        operation_description="""
        Get Model data by Catalog Annotation Template ID.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Catalog Annotation Template ID'
            ),
        ]))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Update Annotation Template',
        operation_description='Update the attributes of an existing labeling task.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Annotation Template ID'
            ),
        ],
        request_body= AnnotationTemplateserializer))
@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Delete Annotation Template',
        operation_description='Delete a task in AiXBlock. This action cannot be undone!',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Annotation Template ID'
            ),
        ],
        ))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Post Catalog Annotation Template',
    operation_description='Perform an action with the selected items from a specific view.',
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Post Catalog Annotation Template',
    operation_description='Perform an action with the selected items from a specific view.',
))
class CatalogAnnotationTemplateAPI(generics.ListCreateAPIView):
    serializer_class = AnnotationTemplateserializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get_queryset(self):
        # Annotation_pk = self.request.query_params.get('Annotation')
        # annotation_pk = self.request.query_params.get('annotation')
        ordering = self.request.query_params.get('ordering')
        return AnnotationTemplate.objects.order_by(ordering)

    def get(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).delete(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).patch(request, *args, **kwargs)

    # @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(AnnotationTemplateAPI, self).put(request, *args, **kwargs)

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Annotation Template'],
        operation_summary='Get Annotation Template List',
        operation_description="Get Annotation Template List.",
))
class CatalogAnnotationTemplateListAPI(generics.ListAPIView):
    serializer_class = AnnotationTemplateserializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )
    pagination_class = SetPagination

    def get_queryset(self):
        return AnnotationTemplate.objects.order_by('-id')
    
    def get(self, request, *args, **kwargs):
        return super(CatalogAnnotationTemplateListAPI, self).get(request, *args, **kwargs)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Post template annotation',
    operation_description='read and import annotation template.',
))
class TemplateListAPI(generics.CreateAPIView):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        configs = import_annotation_templates(user_id)
        return Response(configs, status=200)

@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Update Annotation Template',
    operation_description='Update Annotation Template.',
))
class AnnotationTemplateUpdateAPI(generics.UpdateAPIView):
    serializer_class = AnnotationTemplateserializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_change,
    )
    redirect_kwarg = 'pk'
    queryset = AnnotationTemplate.objects.all()

    def patch(self, request, *args, **kwargs):
        return super(AnnotationTemplateUpdateAPI, self).patch(request, *args, **kwargs)
    
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(AnnotationTemplateUpdateAPI, self).put(request, *args, **kwargs)

@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Annotation Template'],
    operation_summary='Delete Annotation Template Marketplace',
    operation_description='Delete Annotation Template Marketplace.',
))
class AnnotationTemplateDelAPI(generics.DestroyAPIView):
    serializer_class = AnnotationTemplateserializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
    )

    def get_queryset(self):
        return AnnotationTemplate.objects.order_by('-id')

    def delete(self, request, *args, **kwargs):
        super(AnnotationTemplateDelAPI, self).delete(request, *args, **kwargs)
        return Response({"status": "success"}, status=200)


class AnnotationTemplateDetailAPIView(generics.RetrieveAPIView):
    serializer_class = AnnotationDetailTemplateserializer

    def get_queryset(self):
        return AnnotationTemplate.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get("pk"))

        catalog_model_id = obj.catalog_model_id
        if catalog_model_id:
            catalog_model = CatalogModelMarketplace.objects.filter(
                catalog_id=catalog_model_id
            ).first()
            if catalog_model:
                # Update obj with catalog_model
                obj.catalog_model = catalog_model

        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
