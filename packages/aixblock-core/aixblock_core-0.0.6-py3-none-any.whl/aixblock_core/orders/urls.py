from . import api , payment_api
from django.urls import include, path
app_name = 'orders'

_api_urlpatterns = [
    path('', api.OrderAPI.as_view(), name='order-list-create'),
    path('<int:pk>', api.OrderResolveAPI.as_view(), name='order-update'),
    path('<int:pk>/', api.OrderDeleteAPI.as_view(), name='order-delete'),
    path('info-earning', api.InfoEarningAPI.as_view(), name='info-earning')
]


_api_payment_urlpatterns = [
    path('', payment_api.PaymentAPI.as_view(), name='payment-create'),
    path('check/<int:pk>', payment_api.PaymentStatusCheckAPI.as_view(), name='payment-check-status'),
    path('refund', payment_api.RefundAPI.as_view(), name='payment-refund'),
    path('<source_payment>/callback/', payment_api.PaymentCallbackAPI.as_view(), name='payment-callback'),

]

urlpatterns = [
    path('api/payment/', include((_api_payment_urlpatterns, app_name), namespace='api-payment')),
    path('api/orders/', include((_api_urlpatterns, app_name), namespace='api-order')),
]
