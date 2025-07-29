import json
import traceback
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from stripe_payment.functions import capture_payment_intent


@login_required
@require_http_methods(["GET"])
def create_intent(request):
    try:
        # Ref: https://docs.stripe.com/api/payment_intents/create
        pi = stripe.PaymentIntent.create(
            amount=request.GET.get('amount'),
            currency=request.GET.get('currency'),
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never",
            },
            description=f"User {request.user.email} deposit",
            metadata={
                "user_id": request.user.id,
                "email": request.user.email,
            },
            payment_method_configuration=settings.STRIPE_PAYMENT_METHODS_CONFIG,
            receipt_email=request.user.email,
        )
    except Exception as e:
        return HttpResponseBadRequest(content=json.dumps({"detail": e.__str__()}), content_type='application/json')

    return HttpResponse(json.dumps(pi), content_type='application/json')


@login_required
@require_http_methods(["GET"])
def confirm_token(request):
    try:
        # Try to confirm payment
        # Ref: https://docs.stripe.com/api/payment_intents/create
        pi = stripe.PaymentIntent.create(
            confirm=True,
            amount=request.GET.get('amount'),
            currency=request.GET.get('currency'),
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never",
            },
            confirmation_token=request.GET.get('confirmation_token'),
            expand=["latest_charge"],
            description=f"User #{request.user.id} [{request.user.email}] deposit",
            metadata={
                "user_id": request.user.id,
                "email": request.user.email,
            },
            payment_method_configuration=settings.STRIPE_PAYMENT_METHODS_CONFIG,
            receipt_email=request.user.email,
        )

        # If failed to confirm, cancel payment intent
        # Ref: https://docs.stripe.com/api/payment_intents/object#payment_intent_object-status
        if pi["status"] != "succeeded":
            # Handle further confirmation on the client side
            # Ref: https://docs.stripe.com/api/payment_intents/cancel
            # if pi["status"] in ["requires_payment_method", "requires_capture", "requires_confirmation", "requires_action", "processing"]:
            #     stripe.PaymentIntent.cancel(pi["id"])

            return HttpResponseBadRequest(content=json.dumps({
                "detail": "Your payment method needs manual confirmation.",
                "paymentIntent": pi,
            }), content_type='application/json')

        charge = capture_payment_intent(pi["id"])
    except Exception as e:
        if settings.DEBUG:
            traceback.print_exc()

        return HttpResponseBadRequest(content=json.dumps({"detail": e.__str__()}), content_type='application/json')

    return HttpResponse(json.dumps(charge), content_type='application/json')


@login_required
@require_http_methods(["GET"])
def capture(request):
    try:
        charge = capture_payment_intent(request.GET.get('paymentIntent'))
    except Exception as e:
        if settings.DEBUG:
            traceback.print_exc()

        return HttpResponseBadRequest(content=json.dumps({"detail": e.__str__()}), content_type='application/json')

    return HttpResponse(json.dumps(charge), content_type='application/json')
