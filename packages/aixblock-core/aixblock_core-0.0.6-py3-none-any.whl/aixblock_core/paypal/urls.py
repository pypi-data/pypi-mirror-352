"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.urls import path, include
from . import api

app_name = 'paypal'

_api_urlpatterns = [
    path('create-order', api.CreateOrderAPI.as_view(), name='create-order'),
    path('capture-order', api.CaptureOrderAPI.as_view(), name='capture-order'),
]

urlpatterns = [
    path('api/paypal/', include((_api_urlpatterns, app_name), namespace='api-paypal')),
]
