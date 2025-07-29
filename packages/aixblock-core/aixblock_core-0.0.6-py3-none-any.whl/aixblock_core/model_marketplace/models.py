from datetime import date, timedelta, timezone
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from django.contrib.auth import get_user_model
from django.utils import timezone as timezone_django


class DatasetModelMarketplace(models.Model):
    name = models.TextField(_('name'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, null=True)
    owner_id = models.IntegerField(_('owner id'))
    author_id = models.IntegerField(_('author id'))
    catalog_id = models.IntegerField(_('catalog id'))
    project_id = models.IntegerField(_('project id'))
    model_id = models.IntegerField(_('model id'))
    order = models.IntegerField(_('order'))
    config= models.TextField(_('config'))
    dataset_storage_id = models.IntegerField(_('dataset storage id'))
    dataset_storage_name = models.TextField(_('dataset storage name'), null=True)

    type = models.TextField(_('type'),null=True)
    version = models.TextField(_('version'),null=True)
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_marketplace', _('In Marketplace')
        RENTED_BOUGHT = 'rented_bought', _('Rented/Bought')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
        EXPIRED = 'expired', _('Expired')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
        null=True
    )
    file = models.FileField(
        upload_to=settings.DELAYED_EXPORT_DIR,
        null=True,
    )
    def __init__(self, *args, **kwargs):
        super(DatasetModelMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
class CheckpointModelMarketplace(models.Model):
    name = models.TextField(_('name'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'),auto_now=True, null=True)
    owner_id = models.IntegerField(_('owner id'))
    author_id = models.IntegerField(_('author id'))
    checkpoint_storage_id = models.TextField(_('checkpoint storage id'))
    checkpoint_storage_name = models.TextField(_('checkpoint storage name'), null=True)
    ml_id = models.IntegerField(_('ml id'), null=True)
    project_id = models.IntegerField(_('project id'))
    model_id = models.IntegerField(_('model id'))
    catalog_id = models.IntegerField(_('catalog id'), null=True)
    order = models.IntegerField(_('order'))
    config= models.TextField(_('config'))
    type = models.TextField(_('type'))
    version = models.TextField(_('version'))
    file_name = models.TextField(_('file_name'), null=True)
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_marketplace', _('In Marketplace')
        RENTED_BOUGHT = 'rented_bought', _('Rented/Bought')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
        EXPIRED = 'expired', _('Expired')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
    )
    file = models.FileField(
        upload_to=settings.DELAYED_EXPORT_DIR,
        null=True,
    )
    def __init__(self, *args, **kwargs):
        super(CheckpointModelMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self


class ModelTask(models.Model):
    name = models.TextField(_('name'))
    description = models.TextField(_('name'), null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, null=True)

    def __init__(self, *args, **kwargs):
        super(ModelTask, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self

    class Meta:
        db_table = 'model_tasks'


class ModelMarketplace(models.Model):
    name = models.TextField(_("name"))
    model_name = models.TextField(_("model_name"), null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    owner_id = models.IntegerField(_('owner id'))
    author_id = models.IntegerField(_('author id'))
    checkpoint_storage_id = models.TextField(_('checkpoint storage id'), default='')
    ml_id = models.IntegerField(_('ml id'), default=0)
    catalog_id = models.IntegerField(_('catalog id'), default=0)
    order = models.IntegerField(_('order'), default=0)
    config= models.TextField(_('config'), default='cpu,ram,gpu_memory,gpu_card')
    dataset_storage_id = models.IntegerField(_('dataset storage id'), default=0)
    image_dockerhub_id = models.TextField(_('image dockerhub id'),null=True, default='')
    infrastructure_id = models.TextField(_('infrastructure id'),null=True,  default='')
    model_desc = models.TextField(_('model description'),null=True)
    download_count = models.IntegerField(_('download count'),default=0)
    like_count = models.IntegerField(_('like count'),default=0)
    info_run = models.JSONField(_('info run'), null=True, blank=True)
    class Type(models.TextChoices):
        MODELSYSTEM = 'MODEL-SYSTEM', _('MODEL-SYSTEM')
        MODELCUSTOMER = 'MODEL-CUSTOMER', _('MODEL-CUSTOMER')
    type = models.TextField(_('type'), choices=Type.choices, default=Type.MODELCUSTOMER)
    class ModelSource(models.TextChoices):
        HUGGING_FACE = 'HUGGING_FACE', _('HUGGING_FACE')
        ROBOFLOW = "ROBOFLOW", _("ROBOFLOW")
        GIT = "GIT", _("GIT")
        DOCKER_HUB = "DOCKER_HUB", _("DOCKER_HUB")
    model_source = models.TextField(
        _("model_source"), choices=ModelSource.choices, default=ModelSource.DOCKER_HUB
    )

    model_id = models.TextField(
        _("model source id, url"), null=True
    )

    model_token = models.TextField(
        _("model source token"), null=True
    )

    class CheckpointSource(models.TextChoices):
        HUGGING_FACE = "HUGGING_FACE", _("HUGGING_FACE")
        ROBOFLOW = "ROBOFLOW", _("ROBOFLOW")
        GIT = "GIT", _("GIT")
        KAGGLE = "KAGGLE", _("KAGGLE")
        CLOUD_STORAGE = "CLOUD_STORAGE", _("CLOUD_STORAGE")

    checkpoint_source = models.TextField(
        _("checkpoint_source"),
        choices=CheckpointSource.choices,
        default=CheckpointSource.ROBOFLOW,
    )
    ip_address = models.TextField(_('ip_address'),null=True)
    port = models.TextField(_('port'),null=True)
    price = models.FloatField(_('price'), default=0)
    checkpoint_id = models.TextField(_("checkpoint id, url"), null=True)
    checkpoint_token = models.TextField(_("checkpoint token"), null=True)
    compute_gpus = models.JSONField(_('compute_gpus'), default=list)
    is_auto_update_version =models.BooleanField(_(' allow auto update version '), default=False)
    interactive_preannotations = models.BooleanField(_('Use for interactive preannotations'), default=False)

    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_marketplace', _('In Marketplace')
        RENTED_BOUGHT = 'rented_bought', _('Rented/Bought')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
        EXPIRED = 'expired', _('Expired')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
        null=True
    )
    file = models.FileField(
        upload_to=settings.DELAYED_EXPORT_DIR,
        null=True
    )
    docker_image = models.TextField(_("docker_image"), null=True)
    schema = models.TextField(_("schema like: tcp, http, https, grpc"), null=True)
    docker_access_token = models.TextField(_("docker_access_token"), null=True)
    class ModelType(models.TextChoices):
        ADD_MANUAL = "add_manual", _("Add Manual")
        RENT_MARKETPLACE = "rent_marketplace", _("Rent Marketplace")

    model_type = models.CharField(
        _("model_type"),
        max_length=64,
        choices=ModelType.choices,
        default=ModelType.RENT_MARKETPLACE,
        null=True,
    )

    tasks = models.ManyToManyField(ModelTask, related_name='model_marketplaces')

    def __init__(self, *args, **kwargs):
        super(ModelMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return True
    class Meta:
        db_table = 'model_marketplace_model_marketplace'

class CatalogModelMarketplace(models.Model):
    name = models.TextField(_('name'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    catalog_id = models.IntegerField(_('catalog id'), null=True,)
    order = models.IntegerField(_('order'), null=True, default=0)
    tag = models.TextField(_('tag'), null=True)
    key = models.TextField(_('catalog model key'), null=True)
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_marketplace', _('In Marketplace')
        RENTED_BOUGHT = 'rented_bought', _('Rented/Bought')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
        EXPIRED = 'expired', _('Expired')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
        null=True
    )
    file = models.FileField(
        upload_to=settings.DELAYED_EXPORT_DIR,
        null=True,
    )
    def __init__(self, *args, **kwargs):
        super(CatalogModelMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
    class Meta:
        db_table = 'catalog_model_marketplace'

class DownloadModelMarketplace(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True)
    model_id = models.IntegerField(_('model id'))
    user_id = models.IntegerField(_('user id'))
    ip_address = models.TextField(_('ip_address'))
    class Status(models.TextChoices):
        ACTIVED = 'actived', _('Actived')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
        EXPIRED = 'expired', _('Expired')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.PENDING,
        null=True
    )
    def __init__(self, *args, **kwargs):
        super(DownloadModelMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)

class LikeModelMarketplace(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True)
    model_id = models.IntegerField(_('model id'))
    user_id = models.IntegerField(_('user id'))
    ip_address = models.TextField(_('ip_address'))
    class Status(models.TextChoices):
        ACTIVED = 'actived', _('Actived')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
        EXPIRED = 'expired', _('Expired')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.PENDING,
        null=True
    )
    def __init__(self, *args, **kwargs):
        super(LikeModelMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)

class ModelMarketplaceDownload(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    model_id = models.ForeignKey(ModelMarketplace, on_delete=models.CASCADE, db_column='model_id')
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id')
    
    def __init__(self, *args, **kwargs):
        super(ModelMarketplaceDownload, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)
    
    class Meta:
        db_table = 'model_marketplace_download'

class ModelMarketplaceLike(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    model_id = models.ForeignKey(ModelMarketplace, on_delete=models.CASCADE, db_column='model_id')
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id')
    
    
    def __init__(self, *args, **kwargs):
        super(ModelMarketplaceLike, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)
    
    class Meta:
        db_table = 'model_marketplace_like'

class Plan(models.Model):
    SUB_PLAN = (
        ('Basic', 'Basic Plan'),
        ('Gold', 'Gold Plan'),
        ('Platinum', 'Platinum Plan')
    )
    plan_name = models.CharField(max_length=8, choices=SUB_PLAN)
    percent = models.PositiveIntegerField()
    referral_bonus = models.PositiveIntegerField(default=10)
    min = models.DecimalField(max_digits=10, decimal_places=2)
    max = models.DecimalField(max_digits=10, decimal_places=2) 
    duration = models.PositiveIntegerField()
    def __init__(self, *args, **kwargs):
        super(ModelMarketplaceLike, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)
    
    class Meta:
        db_table = 'plan'
class Subscription(models.Model):
    SUB_STATUS =(
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Expired', 'Expired')
    ) 
    SUB_METHOD = (
        ('cash', 'Cash'),
        ('bitcoin', 'Bitcoin'),
        ('card', 'Card')
    )
    SUB_CURRENCY = (
        ('USD', 'USD'),
        ('EURO', 'EURO'),
        ('ETH', 'Ethereum')
    )
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="user")
    type = models.CharField(max_length=10, default="Deposit", editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.DO_NOTHING, related_name="plan")
    sub_method = models.CharField(max_length=24, choices=SUB_METHOD, default='Wallet')
    sub_currency = models.CharField(max_length=12, choices=SUB_CURRENCY, default='Btc')
    sub_amount = models.DecimalField(max_digits=1000, decimal_places=2, default=0.00)
    expires_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=9, choices=SUB_STATUS, default="Pending")
    verified_on = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    initiated_on = models.DateTimeField(auto_now_add=True)
    def __init__(self, *args, **kwargs):
        super(ModelMarketplaceLike, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)

    class Meta:
        db_table = 'subcription'
    def activate_subcription(sender, instance, created, *args, **kwargs):
        if instance.active == True:
            user=instance.user
            status = SUB_STATUS, verified_on = timezone.now()
            expires_at = date.today() + timedelta(days=instance.plan.duration)
            user.balance = instance.sub_amount
            user.save()

# class ModelPrice(models.Model):
#     id = models.AutoField(primary_key=True)
#     model_id = models.ForeignKey(
#         ModelMarketplace, to_field='id', on_delete=models.CASCADE,
#         db_column='model_id', related_name='prices'
#     )
#     token_symbol = models.TextField()
#     price = models.FloatField(default = 0)
#     class Meta:
#         db_table = 'model_price'


class History_Rent_Model(models.Model):
    model_id = models.IntegerField(_("model_id"), default=0)
    model_new_id = models.TextField(_("model_new_id"), default='0')
    project_id = models.IntegerField(_("project_id"), default=0)
    user_id = models.IntegerField(_("user_id"), default=0)
    model_usage = models.IntegerField(_("model_usage"), default=5)
    time_start = models.DateTimeField(_("time_start"), auto_now_add=True)
    time_end = models.DateTimeField(_("time_end"), null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)

    class Status(models.TextChoices):
        RENTING = "renting", _("Renting")
        COMPLETED = "completed", _("Completed")

    status = models.CharField(
        _("status"),
        max_length=64,
        choices=Status.choices,
        default=Status.RENTING,
        null=True,
    )

    class TYPE(models.TextChoices):
        ADD = "add", _("add model")
        RENT = "rent", _("rent model")

    type = models.CharField(
        _("type"),
        max_length=64,
        choices=TYPE.choices,
        default=TYPE.RENT,
        null=True,
        blank=True
    )

    def id(self):
        return id(self.id)

    def __init__(self, *args, **kwargs):
        super(History_Rent_Model, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)

    def check_status(self, *args, **kwargs):
        if self.model_usage == 0:
            self.status = self.Status.COMPLETED

        current_time = timezone_django.now()
        if self.time_end and current_time > self.time_end or current_time.date() > self.created_at.date():
            self.status = self.Status.COMPLETED

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'history_rent_model'


class History_Build_And_Deploy_Model(models.Model):
    version = models.TextField(_("version"), null=True)
    model_id = models.IntegerField(_("model_id"), null=True)
    checkpoint_id = models.IntegerField(_("checkpoint_id"), null=True)
    dataset_id = models.IntegerField(_("dataset_id"), null=True)
    # model_new_id = models.IntegerField(_("model_new_id"), null=True)
    project_id = models.IntegerField(_("project_id"), null=True)
    user_id = models.IntegerField(_("user_id"), null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)

    class TYPE(models.TextChoices):
        BUILD = "build", _("build model")
        DEPLOY = "deploy", _("deploy model")

    type = models.CharField(
        _("type"),
        max_length=64,
        choices=TYPE.choices,
        default=TYPE.BUILD,
        null=True,
        blank=True
    )