import base64
import json
import logging
import uuid

import requests
from django.db import transaction
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings

from compute_marketplace.models import Portfolio
from paypal import serializers

raw_token = bytes(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}", 'utf-8')
basic_token = base64.b64encode(raw_token).decode('utf-8')


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["PayPal"],
        operation_summary="Create PayPal order",
        request_body=serializers.CreateOrderSerializer,
    ),
)
class CreateOrderAPI(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            req = requests.post(
                settings.PAYPAL_ENDPOINT + "/v2/checkout/orders",
                headers={
                    "Authorization": "Basic " + basic_token,
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "intent": "CAPTURE",
                    "purchase_units": [
                        {
                            "reference_id": str(uuid.uuid4()),
                            "amount": {
                                "currency_code": "USD",
                                "value": round(serializer.data["amount"], 2),
                            }
                        }
                    ],
                    "payment_source": {
                        "paypal": {
                            "experience_context": {
                                "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                                "brand_name": "AIxBlock",
                                "locale": "en-US",
                                "landing_page": "LOGIN",
                                "shipping_preference": "NO_SHIPPING",
                                "user_action": "PAY_NOW",
                            }
                        }
                    }
                })
            )

            data = req.json()

            if not req.ok:
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(e)
            return Response({"message": e.__str__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["PayPal"],
        operation_summary="Capture PayPal order after customer completed the payment",
        request_body=serializers.CaptureOrderSerializer,
    ),
)
class CaptureOrderAPI(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.CaptureOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            req = requests.post(
                settings.PAYPAL_ENDPOINT + "/v2/checkout/orders/" + serializer.data["order_id"] + "/capture",
                headers={
                    "Authorization": "Basic " + basic_token,
                    "Content-Type": "application/json",
                }
            )

            data = req.json()

            if not req.ok:
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(e)
            return Response({"message": e.__str__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        amount = float(data["purchase_units"][0]["payments"]["captures"][0]["seller_receivable_breakdown"]["net_amount"]["value"])

        with transaction.atomic():
            user = request.user
            portfolio = Portfolio.objects.select_for_update().filter(account=user).filter(token_symbol="USD").first()

            if portfolio is not None:
                portfolio.amount_holding += amount
                portfolio.save()
            else:
                Portfolio.objects.create(
                    account=user,
                    token_symbol="USD",
                    token_name="United States Dollar",
                    amount_holding=amount,
                )

        return Response(data, status=status.HTTP_200_OK)
