from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from compute_marketplace.models import Trade
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer, OrderFilter, TradePaymentSerializer
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from core.filters import filterModel
from core.swagger_parameters import (
    page_parameter,
    search_parameter,
    field_search_parameter,
    sort_parameter,
    type_parameter,
)
from aixblock_core.core.utils.params import get_env
from core.permissions import ViewClassPermission, all_permissions
from core.utils.paginate import SetPagination
from django_filters.rest_framework import DjangoFilterBackend
from aixblock_core.core.utils.params import get_env
import requests
from rest_framework.response import Response
import drf_yasg.openapi as openapi
from reward_point.models import User_Point
from coinbase_commerce.client import Client

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Payment'],
    operation_summary='Create payment',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'payment_method': openapi.Schema(type=openapi.TYPE_STRING, description='Payment method'),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Payment amount'),
            'price': openapi.Schema(type=openapi.TYPE_STRING, description='Price'),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type'),
            'resource': openapi.Schema(type=openapi.TYPE_STRING, description='Resource'),
            'resource_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Resource ID'),
            'order_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Order ID'),
            'reward_points_used': openapi.Schema(type=openapi.TYPE_INTEGER, description='reward points used'),
        },
        required=['payment_method', 'amount', 'price', 'type', 'resource', 'resource_id', 'order_id']
    )
))
class PaymentAPI(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        payment_method = request.data.get('payment_method')
        amount = request.data.get('amount')
        price = float(request.data.get('price'))
        type = request.data.get('type') 
        resource = request.data.get('resource')
        resource_id = request.data.get('resource_id')
        order_id = request.data.get('order_id') 
        reward_points_used = request.data.get('reward_points_used') 

        user = request.user
        user_point = get_object_or_404(User_Point, user = user)
        order = get_object_or_404(Order, id=order_id)
        
        # Check payment
        # payment_method -> not reward_points_used
        if reward_points_used:
                price -= reward_points_used #Config point -> price
                user_point.point -= reward_points_used
                user_point.save()

        if payment_method == 'reward':
            if user_point.point >= price:
                user_point.point -= price
                reward_points_used = price
                price = 0
                user_point.save()
            else:
                return Response({'message': 'Not enough points'}, status=status.HTTP_400_BAD_REQUEST)
        # Other method

        # Payment done - create trade
        trade = Trade.objects.create(
            account = user,
            payment_method=payment_method,
            amount=amount,
            price=price,
            type=type,
            resource=resource,
            resource_id=resource_id,
            order=order_id,
            reward_points_used=reward_points_used
        )

        # Serialize the created trade
        serializer = TradePaymentSerializer(trade)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Payment'],
    operation_summary='Check Payment Status',
    operation_description='Retrieve the status of a payment',
))
class PaymentStatusCheckAPI(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
      
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Payment'],
    operation_summary='Refund Payment',
    operation_description='Cancel and refund an order',
))
class RefundAPI(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'canceled'
        instance.save()
        return Response({"status": "success", "message": "Order refunded"}, status=status.HTTP_200_OK)
 
 
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Payment'],
    operation_summary='Payment Callback when is payment successfully',
    operation_description='call back',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'payment_method': openapi.Schema(type=openapi.TYPE_STRING, description='Payment method'),
            'order_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Order ID'),
        },
        required=['payment_method','order_id']
    )
))
class PaymentCallbackAPI(generics.CreateAPIView):
    def post(self, request, source_payment, *args, **kwargs):
        if source_payment == 'moonpay':
            # Xử lý đơn hàng theo Moonpay
            # Thực hiện các hành động cần thiết, như cập nhật trạng thái đơn hàng, tạo giao dịch, vv.
            # order_id = request.data.get('order_id')
            # order = get_object_or_404(Order, id=order_id)
            # order.status = 'paid'
            # order.save()
            return Response({"message": "Order processed successfully."}, status=status.HTTP_200_OK)
        elif source_payment == 'coinbase':
            order_id = request.data.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            client = Client(api_key="api-key")  #Get key from https://beta.commerce.coinbase.com/settings/security
            
            # # Check error 
            # for charge in client.charge.list_paging_iter():
            #     print("{!r}".format(charge))

            domain_url = 'http://localhost:8080/'

            product = {
                'name': 'Name Product Order', #order.compute_marketplace.name | order.model_marketplace.name,
                'description': 'Description',
                'local_price': {
                    'amount': f'{order.total_amount}',
                    'currency': 'USD' #Type Coin
                },
                'pricing_type': 'fixed_price',
                'redirect_url': domain_url + 'success/',
                'cancel_url': domain_url + 'cancel/',
                # 'metadata': {
                #     'customer_id': request.user.id if request.user.is_authenticated else None,
                #     'customer_username': request.user.username if request.user.is_authenticated else None,
                # },
            }
            charge = client.charge.create(**product)
            
            print(charge.hosted_url) #: Page for payment

            data = {
                "success": True,
                "status_code": 200,
                "msg": "Order processed successfully."
            }
            
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"Unsupported source payment: {source_payment}"}, status=status.HTTP_400_BAD_REQUEST)