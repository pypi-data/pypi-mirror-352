from django.db import models
from users.models import User
from orders.models import Order

# Create your models here.
class Action_Point(models.Model):
    name = models.TextField(null=True, blank=True)
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    description = models.TextField(null=True, blank=True)
    activity = models.CharField(max_length=255,null=False)
    point = models.IntegerField(default = 0)
    detail = models.TextField(null=True, blank=True)
    customer = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Action_Point, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
class User_Action_History(models.Model):
    user = models.ForeignKey(User, related_name='user_action_history', on_delete=models.CASCADE)
    action =  models.ForeignKey(Action_Point, related_name='user_action_history', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='user_action_history', on_delete=models.CASCADE, null = True)
    point = models.IntegerField(default = 0)
    status = models.IntegerField(default = 0) ## 0 - Add point   1- Minus point
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.IntegerField(null= True)
    note = models.TextField(null=True, blank=True)

class User_Point(models.Model):
    user = models.ForeignKey(User, related_name='user_point', on_delete=models.CASCADE)
    point = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)