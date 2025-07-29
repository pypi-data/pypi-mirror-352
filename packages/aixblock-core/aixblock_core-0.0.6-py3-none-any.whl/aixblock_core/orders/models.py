from django.db import models
from compute_marketplace.models import ComputeMarketplace, ComputeGPU
from model_marketplace.models import ModelMarketplace
from users.models import User
import uuid

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('refund', "Refund")
    )

    UNIT_CHOICES = (
        ('USD', 'US Dollar'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'ethereum'),
        ('point', 'Reward Point'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('wallet', 'Electronic Wallet'),
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('reward', 'Reward Point'),
    )

    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='reward')
    payment_code = models.CharField(max_length=100, blank=True, null=True)  # unique
    service_fee = models.CharField(max_length=100, null=True)
    reward_points_used = models.IntegerField(default=0, null=True)
    model_marketplace = models.ForeignKey(ModelMarketplace, related_name='orders', on_delete=models.CASCADE, null=True)
    compute_gpus = models.ManyToManyField(ComputeGPU, through='OrderComputeGPU', related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    payer_email = models.CharField(max_length=100, null=False, default="")
    payer_full_name = models.CharField(max_length=100, null=False, default="")

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        if not self.payment_code:
            self.payment_code = str(uuid.uuid4())
    def has_permission(self, user):
        return self

class OrderInfrastructure(models.Model):
    order = models.ForeignKey(Order, related_name='order', on_delete=models.CASCADE)
    infrastructure_id = models.CharField(max_length=100, null=False)

    class Meta:
        unique_together = ("order", "infrastructure_id")

class OrderComputeGPU(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    compute_gpu = models.ForeignKey(ComputeGPU, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("order", "compute_gpu")
