import requests
import uuid
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
# from .models import TutorialGroup, TutorialContent, TutorialSectionContent, TutorialSubGroup,
# TutorialGroupSerializer, TutorialSubGroupSerializer, TutorialSectionContentSerializer, TutorialContentSerializer,
from .serializers import  \
    DocumentPageListSerializer, DocumentBlockSerializer
from django.db.models import Q
import drf_yasg.openapi as openapi
from .common import NOTION_API_HEADERS, NOTION_API_URL, NOTION_CLIENT_HEADER, NOTION_CLIENT_API_URL
from .utils import structure_pages, get_page_section


# @method_decorator(
#     name='get',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='List all Tutorials',
#         manual_parameters=[
#             openapi.Parameter(
#                 name='keyword',
#                 type=openapi.TYPE_STRING,
#                 in_=openapi.IN_QUERY,
#             ),
#         ]
#     ),
# )
# class TutorialListApi(generics.ListAPIView):
#     serializer_class = TutorialGroupSerializer
#     def get_queryset(self):
#         keyword = self.request.query_params.get('keyword')
#         if keyword:
#             return TutorialGroup.objects.filter(
#                 Q(sub_groups__section_contents__tutorial_content__content__icontains=keyword)
#             ).all()
#         return TutorialGroup.objects.all().order_by('order', 'id')

#     def get(self, request, *args, **kwargs):
#         return super(TutorialListApi, self).get(request, *args, **kwargs)

# @method_decorator(
#     name='get',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='List all Tutorial Groups',
#     ),
# )
# class TutorialGroupListApi(generics.ListAPIView):
#     serializer_class = TutorialGroupSerializer

#     def get_queryset(self):
#         return TutorialGroup.objects.all().order_by('order', 'id')

#     def get(self, request, *args, **kwargs):
#         return super(TutorialGroupListApi, self).get(request, *args, **kwargs)

# @method_decorator(
#     name='post',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Create Tutorial Group',
#     ),
# )
# class TutorialGroupCreateApi(generics.CreateAPIView):
#     serializer_class = TutorialGroupSerializer

#     def post(self, request, *args, **kwargs):
#         return super(TutorialGroupCreateApi, self).post(request, *args, **kwargs)
    
# @method_decorator(
#     name='patch',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Update Tutorial Group',
#     ),
# )
# class TutorialGroupUpdateApi(generics.UpdateAPIView):
#     serializer_class = TutorialGroupSerializer
#     get_queryset = TutorialGroup.objects.all

#     def patch(self, request, *args, **kwargs):
#         return super(TutorialGroupUpdateApi, self).patch(request, *args, **kwargs)
    
#     @swagger_auto_schema(auto_schema=None)
#     def put(self, request, *args, **kwargs):
#         return super(TutorialGroupUpdateApi, self).put(request, *args, **kwargs)

# @method_decorator(
#     name='delete',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Delete Tutorial Group',
#     ),
# )
# class TutorialGroupDeleteApi(generics.DestroyAPIView):
#     serializer_class = TutorialGroupSerializer
#     get_queryset = TutorialGroup.objects.all

#     def delete(self, request, *args, **kwargs):
#         return super(TutorialGroupDeleteApi, self).delete(request, *args, **kwargs)

# @method_decorator(
#     name='get',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='List all Tutorial Subgroups',
#     ),
# )
# class TutorialSubgroupListApi(generics.ListAPIView):
#     serializer_class = TutorialSubGroupSerializer
#     get_queryset = TutorialSubGroup.objects.all

#     def get(self, request, *args, **kwargs):
#         return super(TutorialSubgroupListApi, self).get(request, *args, **kwargs)

# @method_decorator(
#     name='post',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Create Tutorial Sub Group',
#     ),
# )
# class TutorialSubgroupCreateApi(generics.CreateAPIView):
#     serializer_class = TutorialSubGroupSerializer

#     def post(self, request, *args, **kwargs):
#         return super(TutorialSubgroupCreateApi, self).post(request, *args, **kwargs)

# @method_decorator(
#     name='patch',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Update Tutorial Sub Group',
#     ),
# )
# class TutorialSubgroupUpdateApi(generics.UpdateAPIView):
#     serializer_class = TutorialSubGroupSerializer
#     get_queryset = TutorialSubGroup.objects.all

#     def patch(self, request, *args, **kwargs):
#         return super(TutorialSubgroupUpdateApi, self).patch(request, *args, **kwargs)
    
#     @swagger_auto_schema(auto_schema=None)
#     def put(self, request, *args, **kwargs):
#         return super(TutorialSubgroupUpdateApi, self).put(request, *args, **kwargs)

# @method_decorator(
#     name='delete',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Delete Tutorial Subgroup',
#     ),
# )
# class TutorialSubgroupDeleteApi(generics.DestroyAPIView):
#     serializer_class = TutorialSubGroupSerializer
#     get_queryset = TutorialSubGroup.objects.all

#     def delete(self, request, *args, **kwargs):
#         return super(TutorialSubgroupDeleteApi, self).delete(request, *args, **kwargs)
    
# @method_decorator(
#     name='get',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='List all Tutorial Sections',
#     ),
# )
# class TutorialSectionContentListApi(generics.ListAPIView):
#     serializer_class = TutorialSectionContentSerializer
#     get_queryset = TutorialSectionContent.objects.all

#     def get(self, request, *args, **kwargs):
#         return super(TutorialSectionContentListApi, self).get(request, *args, **kwargs)
    
# @method_decorator(
#     name='post',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Create Tutorial Section Content',
#     ),
# )
# class TutorialSectionContentCreateApi(generics.CreateAPIView):
#     serializer_class = TutorialSectionContentSerializer

#     def post(self, request, *args, **kwargs):
#         return super(TutorialSectionContentCreateApi, self).post(request, *args, **kwargs)

# @method_decorator(
#     name='patch',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Update Tutorial Section Content',
#     ),
# )
# class TutorialSectionContentUpdateApi(generics.UpdateAPIView):
#     serializer_class = TutorialSectionContentSerializer
#     get_queryset = TutorialSectionContent.objects.all

#     def patch(self, request, *args, **kwargs):
#         return super(TutorialSectionContentUpdateApi, self).patch(request, *args, **kwargs)
    
#     @swagger_auto_schema(auto_schema=None)
#     def put(self, request, *args, **kwargs):
#         return super(TutorialSectionContentUpdateApi, self).put(request, *args, **kwargs)

# @method_decorator(
#     name='delete',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Delete Tutorial Section',
#     ),
# )
# class TutorialSectionContentDeleteApi(generics.DestroyAPIView):
#     serializer_class = TutorialSectionContentSerializer
#     get_queryset = TutorialSectionContent.objects.all

#     def delete(self, request, *args, **kwargs):
#         return super(TutorialSectionContentDeleteApi, self).delete(request, *args, **kwargs)

# @method_decorator(
#     name='post',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Create Tutorial Content',
#     ),
# )
# class TutorialContentCreateApi(generics.CreateAPIView):
#     serializer_class = TutorialContentSerializer

#     def post(self, request, *args, **kwargs):
#         return super(TutorialContentCreateApi, self).post(request, *args, **kwargs)

# @method_decorator(
#     name='patch',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Update Tutorial Content',
#     ),
# )
# class TutorialContentUpdateApi(generics.UpdateAPIView):
#     serializer_class = TutorialContentSerializer
#     get_queryset = TutorialContent.objects.all

#     def patch(self, request, *args, **kwargs):
#         return super(TutorialContentUpdateApi, self).patch(request, *args, **kwargs)
    
#     @swagger_auto_schema(auto_schema=None)
#     def put(self, request, *args, **kwargs):
#         return super(TutorialContentUpdateApi, self).put(request, *args, **kwargs)

# @method_decorator(
#     name='delete',
#     decorator=swagger_auto_schema(
#         tags=['Tutorial API'],
#         operation_summary='Delete Tutorial Content',
#     ),
# )
# class TutorialContentDeleteApi(generics.DestroyAPIView):
#     serializer_class = TutorialContentSerializer
#     get_queryset = TutorialContent.objects.all

#     def delete(self, request, *args, **kwargs):
#         return super(TutorialContentDeleteApi, self).delete(request, *args, **kwargs)
    

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Document API'],
        operation_summary='Get List Document Pages',
    ),
)
class DocumentPagesListGetApi(generics.RetrieveAPIView):
    serializer_class = DocumentPageListSerializer(many=True)

    def get(self, request):
        response = requests.post(
            url=f'{NOTION_API_URL}/search', 
            headers=NOTION_API_HEADERS,
        )
        restructured_page = structure_pages(response.json().get("results", []))
        return JsonResponse({"documents": restructured_page})
    

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Document API'],
        operation_summary='Get Document Page',
    ),
)
class DocumentPageGetApi(generics.RetrieveAPIView):
    serializer_class = DocumentBlockSerializer(many=True)

    def get(self, request, id):

        response = requests.post(url=f"{NOTION_CLIENT_API_URL}/loadPageChunk",
            headers=NOTION_CLIENT_HEADER,
            json={
                "pageId": str(uuid.UUID(id)),
                "limit": 100,
                "chunkNumber": 0,
                "verticalColumns": False,
                "cursor": {
                    'stack': [] 
                }
            }
        )
        page = response.json()
        page["page_sections"] = get_page_section(page["recordMap"].get("block") or {})
        return JsonResponse(page)
    