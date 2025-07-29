import time
import traceback

import stripe
from django.conf import settings
from django.db import transaction
from compute_marketplace.models import Portfolio
from users.models import User


def capture_payment_intent(payment_intent_id) -> stripe.Charge:
    # Refresh payment intent
    # Ref: https://docs.stripe.com/api/payment_intents/retrieve
    pi = stripe.PaymentIntent.retrieve(payment_intent_id)

    if pi["status"] != "succeeded":
        raise Exception("The payment transaction is not completed")

    try:
        if pi["metadata"]["collected"]:
            raise Exception("The payment has been processed already")
    except:
        if settings.DEBUG:
            traceback.print_exc()

    # Get charge to retrieve the amount after deducted the fee
    # Ref: https://docs.stripe.com/api/charges/retrieve
    charge = None
    try_count = 0

    while not charge or not charge["balance_transaction"]:
        charge = stripe.Charge.retrieve(pi["latest_charge"], expand=["balance_transaction"])
        time.sleep(3)
        try_count += 1

        if try_count >= 3:
            break

    if not charge:
        raise Exception("The balance transaction not found")

    # Ref: https://docs.stripe.com/api/balance_transactions/object#balance_transaction_object-net
    net_amount = int(charge["balance_transaction"]["net"]) / 100

    with transaction.atomic():
        portfolio = Portfolio.objects.select_for_update().filter(account_id=pi["metadata"]["user_id"]).filter(token_symbol="USD").first()

        if portfolio is not None:
            portfolio.amount_holding += net_amount
            portfolio.save()
        else:
            Portfolio.objects.create(
                account=User.objects.filter(pk=pi["metadata"]["user_id"]).first(),
                token_symbol="USD",
                token_name="United States Dollar",
                amount_holding=net_amount,
            )

        stripe.PaymentIntent.modify(pi["id"], metadata={
            "collected": True,
            "collected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return charge
