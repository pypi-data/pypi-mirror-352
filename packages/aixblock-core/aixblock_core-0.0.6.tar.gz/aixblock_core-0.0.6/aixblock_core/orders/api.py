from rest_framework import generics, status
from .models import Order
from .serializers import OrderSerializer, OrderFilter
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from core.filters import filterModel
from core.swagger_parameters import page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter
from aixblock_core.core.utils.params import get_env
from core.permissions import ViewClassPermission, all_permissions
from core.utils.paginate import SetPagination
from django_filters.rest_framework import DjangoFilterBackend
from aixblock_core.core.utils.params import get_env
import requests
from rest_framework.response import Response
import drf_yasg.openapi as openapi
from django.utils import timezone
from compute_marketplace.models import History_Rent_Computes, ComputeMarketplace

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Order'],
        operation_summary='Get List Orders',
        operation_description="Get List Orders",
        manual_parameters=[page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter]
    ))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Order'],
    operation_summary='Post Orders',
      operation_description='''
        STATUS = (
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled'),
        )
        
        UNIT = (
            ('USD', 'US Dollar'),
            ('BTC', 'Bitcoin'),
            ('ETH', 'Ethereum'),
            ('point', 'Reward Point'),
        )
        
        PAYMENT_METHOD = (
            ('wallet', 'Electronic Wallet'),
            ('visa', 'Visa'),
            ('mastercard', 'MasterCard'),
            ('reward', 'Reward Point'),
        )
        ''',
    
))
class OrderAPI(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.orders_view,
        POST=all_permissions.orders_create,
    )
    pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]
    # filterset_class = OrderFilter
    
    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return super(OrderAPI, self).post(request, *args, **kwargs)
    
    def get_queryset(self):
        order_ids = History_Rent_Computes.objects.filter(account_id=self.request.user.id).values_list("order_id", flat=True)
        queryset = Order.objects.prefetch_related(
            'compute_gpus',
            'compute_gpus__compute_marketplace',
            'compute_gpus__history_rent_computes'
        ).filter(id__in=order_ids).order_by("-created_at")
        return queryset


    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

@method_decorator(name='put', decorator=swagger_auto_schema(
        tags=['Order'],
        operation_summary='update Orders',
        operation_description="update Orders",
        request_body= OrderSerializer
    ))

@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Order'],
        operation_summary='Update Order',
        operation_description='Update Order',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                description='Order ID'
            ),
        ],
        request_body= OrderSerializer))

class OrderResolveAPI(generics.UpdateAPIView):
    serializer_class = OrderSerializer 
    permission_required = ViewClassPermission(
        PATCH=all_permissions.orders_change,
    )

    def get_queryset(self):
        order_pk = self.kwargs.get('pk')
        return Order.objects.filter(id=order_pk)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Order'],
    operation_summary='Soft Delete Order',
    operation_description='Soft Delete Order!',
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_STRING,
            in_=openapi.IN_PATH,
            description='Order ID'
        ),
    ],
))
class OrderDeleteAPI(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    permission_required = ViewClassPermission(
        DELETE=all_permissions.orders_delete,
    )

    def get_queryset(self):
        order_pk = self.kwargs.get('pk')
        return Order.objects.filter(id=order_pk, deleted_at__isnull=True)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order.deleted_at = timezone.now()  
        order.save()
        return Response({"status": "success", "message": "Order soft deleted"}, status=status.HTTP_204_NO_CONTENT)

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Order'],
        operation_summary='Get List info earning',
        operation_description="Get List info earning",
        # manual_parameters=[page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter]
    ))

class InfoEarningAPI(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.orders_view,
        # POST=all_permissions.orders_create,
    )
    # pagination_class = SetPagination
    filter_backends = [DjangoFilterBackend]
    # filterset_class = OrderFilter
    
    def get_queryset(self):
        queryset = Order.objects.all()
        return filterModel(self, queryset, Order)


    def get(self, request, *args, **kwargs):
        user = request.user
        total_earning = 0
        hours_serverd = 0
        compute_serverd = 0
        pending_earning = 0
        slashed = 0

        computes_renting = ComputeMarketplace.objects.filter(owner_id = user.id, deleted_at__isnull=True).values_list("id", flat=True)
        history_rent = History_Rent_Computes.objects.filter(compute_marketplace_id__in = computes_renting, status="renting", compute_install=History_Rent_Computes.InstallStatus.COMPLETED, deleted_at__isnull=True).exclude(account_id=user.id)
        history_done = History_Rent_Computes.objects.filter(compute_marketplace_id__in = computes_renting, status="completed", compute_install=History_Rent_Computes.InstallStatus.COMPLETED, deleted_at__isnull=False).exclude(account_id=user.id)
        
        compute_serverd = history_rent.count() + history_done.count()

        for history in history_rent:
            order_instance = Order.objects.filter(id=history.order_id).first()
            if order_instance:
                price = float(order_instance.price)
                time_rent = (timezone.now() - history.time_start).total_seconds() / 3600
                hours_serverd += time_rent
                amount = float(price * time_rent)
                pending_earning += amount
        
        for history in history_done:
            order_instance = Order.objects.filter(id=history.order_id).first()
            if order_instance:
                price = float(order_instance.price)
                if history.time_end < history.deleted_at:
                    time_rent = (history.time_end - history.time_start).total_seconds() / 3600
                else:
                    time_rent = (history.deleted_at - history.time_start).total_seconds() / 3600
                hours_serverd += time_rent
                amount = float(price * time_rent)
                total_earning += amount


        data = {
            "Total Earning": total_earning,
            "Hours Served": hours_serverd,
            "Compute Served": compute_serverd,
            "Pending Earnings": pending_earning,
            "Slashed": 0
        }
        return Response(data)