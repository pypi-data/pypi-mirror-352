from datetime import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User, Notification
from projects.models import Project
from model_marketplace.models import ModelMarketplace
from django_rq import job
import jwt

class ComputeMarketplace(models.Model):
    name = models.TextField(_('name'), default='')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True)
    infrastructure_id = models.TextField(_('infrastructure_id'), unique=True)
    owner_id = models.IntegerField(_('owner_id'))
    author_id = models.IntegerField(_('author_id'))
    catalog_id = models.IntegerField(_('catalog_id'), default=0)
    organization_id = models.IntegerField(_('organization_id'))
    order = models.IntegerField(_('order'), default=0)
    infrastructure_desc = models.TextField(_('infrastructure_desc'), default='')
    ip_address = models.TextField(_('ip_address'))
    port = models.TextField(_('port'), default="8080")
    docker_port = models.TextField(_('docker_port'), default="4243")
    kubernetes_port = models.TextField(_('kubernetes_port'), default="6443")
    config = models.JSONField(_("config"), null=True, blank=True)
    is_using_cpu = models.BooleanField(_('is_using_cpu'),default=False, null=True)
    is_scale = models.BooleanField(_('is_scale'),default=False, null=True)
    project_id = models.IntegerField(_('project_id'), null=True)
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_marketplace', _('In Marketplace')
        RENTED_BOUGHT = 'rented_bought', _('Rented/Bought')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUSPEND = 'suspend', _('Suspend')
        EXPIRED = 'expired', _('Expired')
        FAILED = 'failed', _('Failed') # install failed
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
    )
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    file = models.FileField(
        upload_to=settings.DELAYED_EXPORT_DIR,
        null=True,
    )
    class Type(models.TextChoices):
        MODELSYSTEM = 'MODEL-SYSTEM', _('MODEL-SYSTEM')
        MODELCUSTOMER = 'MODEL-CUSTOMER', _('MODEL-CUSTOMER')
        COMPUTE_SELF_HOST = "COMPUTE-SELF-HOST", _("COMPUTE_SELF_HOST")
        PROVIDERVAST = "MODEL-PROVIDER-VAST", _("MODEL-PROVIDER-VAST")
        PROVIDEREXABIT = "MODEL-PROVIDER-EXABIT", _("MODEL-PROVIDER-EXABIT")
        
    type = models.TextField(_('type'), choices=Type.choices, default=Type.MODELCUSTOMER)
    infrastructure_desc = models.TextField(_('infrastructure_desc'), default='')

    callback_url = models.TextField(_('callback_url'), default='')
    client_id = models.TextField(_('client_id'))
    client_secret = models.TextField(_('client_secret'))
    ssh_key = models.TextField(_('ssh_key'), null=True)
    card = models.IntegerField(_('card'), null=True)
    price = models.FloatField(_('price'), null=True, default=0)
    compute_type = models.TextField(_('compute_type'), null=True)
    location_id = models.IntegerField(_("location_id"), blank=True, null=True)
    location_alpha2 = models.TextField(_("location_alpha2 ex: vn"), blank=True, null=True)
    location_name = models.TextField(
        _("location_name ex: Viet Nam"), blank=True, null=True
    )
    username = models.TextField(
        _("storage user name"), blank=True, null=True, editable=False
    )
    password = models.TextField(
        _("storage password"), blank=True, null=True, editable=False
    )
    api_port = models.TextField(_("api port"), null=True)

    def __init__(self, *args, **kwargs):
        super(ComputeMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self

    def get_filtered_compute_gpus(self):
        return self.compute_gpus.filter(deleted_at__isnull=True).exclude(
            status="been_removed"
        )
    def set_password(self, raw_password):
        encoded_password = jwt.encode({'password': raw_password}, settings.MINIO_SECRET_KEY, algorithm='HS256')
        self.password = encoded_password

    def get_password(self):
        decoded_password = jwt.decode(self.password, settings.MINIO_SECRET_KEY, algorithms=['HS256'])
        return decoded_password['password']

    class Meta:
        db_table = 'compute_marketplace_compute_marketplace'

class CatalogComputeMarketplace(models.Model):
    name = models.TextField(_('name'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    catalog_id = models.IntegerField(_('catalog id'), null=True)
    order = models.IntegerField(_('order'), default=0, null=True)
    tag = models.TextField(_('tag'), null=True)
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
        super(CatalogComputeMarketplace, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
    class Meta:
        db_table = 'catalog_compute_marketplace'

class Trade(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('wallet', 'Electronic Wallet'),
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('reward', 'Reward Point'),
        ('cryto', 'Cryto')
    )
    token_name = models.CharField(max_length=100)
    token_symbol = models.CharField(max_length=10)
    date = models.DateTimeField( auto_now_add=True)
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trader')
    amount = models.FloatField()
    price = models.FloatField()
    cost = models.FloatField(default=0, verbose_name='cost of payment with blockchain', null=True)
    type = models.CharField(max_length=15,
                              choices=(
                                  ("Market Fund", "Market Fund"),
                                  ("Market Withraw", "Market Withraw")))
    # compute_gpu_id = models.IntegerField()
    class Status(models.TextChoices):
        RENTING = 'renting', _('Renting')
        COMPLETED = 'completed', _('Completed')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.RENTING,
        null=True
    )
    resource = models.CharField(max_length=50, null=True) 
    resource_id = models.IntegerField(null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='reward')
    order = models.IntegerField(_('order'), null=True) # orders id fk to order
    wallet_address = models.CharField(max_length=500, null=True)

    def id(self):
        return id(self.id)
    def __init__(self, *args, **kwargs):
        super(Trade, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)
    class Meta:
        db_table = 'trade'

class Portfolio(models.Model):
    token_name = models.CharField(max_length=100, default="United States Dollar")
    token_symbol = models.CharField(max_length=10, default="USD")
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio')
    amount_holding = models.FloatField(default="100000")

    def id(self):
        return id(self.id)
    def __init__(self, *args, **kwargs):
        super(Portfolio, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self.project.has_permission(user)
    class Meta:
        db_table = 'portfolio'

class ComputeGPU(models.Model):
    id = models.AutoField(primary_key=True)

    compute_marketplace = models.ForeignKey(ComputeMarketplace, related_name='computegpus', on_delete=models.CASCADE)
    infrastructure_id = models.ForeignKey(
        ComputeMarketplace, to_field='infrastructure_id', on_delete=models.SET_NULL, null=True,
        db_column='infrastructure_id', related_name='compute_gpus'
    )

    gpu_name = models.TextField(_('gpu_name'), null=True)
    power_consumption = models.TextField(_('power_consumption'), blank=True, null=True)
    memory_usage = models.TextField(_('memory_usage'), blank=True, null=True)
    power_usage = models.TextField(_('power_usage'), blank=True, null=True)
    gpu_index = models.IntegerField(_('gpu_index'), default=0)
    gpu_memory = models.TextField(
        _("total memory convert to bytes"), blank=True, null=True
    )
    memory = models.TextField(
        _("memory for gpu convert to bytes"), blank=True, null=True
    )
    gpu_memory_used = models.TextField(
        _("gpu_memory_used convert to Bytes"), blank=True, null=True
    )
    gpu_memory_bandwidth = models.TextField(
        _("gpu_memory_bandwidth convert to Bytes"), blank=True, null=True
    )
    disk_bandwidth = models.TextField(
        _("disk_bandwidth convert to Bytes"), blank=True, null=True
    )
    motherboard = models.TextField(_("motherboard "), blank=True, null=True)
    internet_up_speed = models.TextField(
        _("internet_up_speed convert to Mbps"), blank=True, null=True
    )
    internet_down_speed = models.TextField(
        _("internet_down_speed convert to Mbps"), blank=True, null=True
    )  
    number_of_pcie_per_gpu = models.TextField(
        _("number_of_pcie_per_gpu ex:4.0,16x"), blank=True, null=True
    ) 
    per_gpu_pcie_bandwidth = models.TextField(
        _("per_gpu_pcie_bandwidth convert to bytes"), blank=True, null=True
    )
    eff_out_of_total_nu_of_cpu_virtual_cores = models.TextField(
        _("eff_out_of_total_nu_of_cpu_virtual_cores ex:42.7/128 "),
        blank=True,
        null=True,
    )
    cores = models.TextField(
        _("cores"),
        blank=True,
        null=True,
    )
    cuda_cores = models.TextField(
        _("cuda_cores"),
        blank=True,
        null=True,
    )
    memory_bus_width = models.TextField(
        _("memory_bus_width"),
        blank=True,
        null=True,
    )

    gpu_clock_mhz = models.TextField(
        _("gpu_clock_mhz"),
        blank=True,
        null=True,
    )

    mem_clock_mhz = models.TextField(
        _("mem_clock_mhz"),
        blank=True,
        null=True,
    )

    disk = models.TextField(
        _("disk"),
        blank=True,
        null=True,
    )

    disk_used = models.TextField(
        _("disk_used"),
        blank=True,
        null=True,
    )

    disk_free = models.TextField(
        _("disk_free"),
        blank=True,
        null=True,
    )

    eff_out_of_total_system_ram = models.TextField(
        _("eff_out_of_total_system_ram ex:86/258 convert to GB "),
        blank=True,
        null=True,
    )
    max_cuda_version = models.TextField(
        _("max cuda version"), blank=True, null=True
    )
    driver_version = models.TextField(_("driver_version"), blank=True, null=True)
    ubuntu_version = models.TextField(_("ubuntu_version"), blank=True, null=True)
    reliability = models.FloatField(_("reliability"), blank=True, null=True, default=100)
    dl_performance_score = models.FloatField(
        _("dl_performance_score"), blank=True, null=True
    )
    dlp_score = models.FloatField(
        _("dlp_score"), blank=True, null=True
    )
    location_id = models.IntegerField(_("location_id"), blank=True, null=True)
    location_alpha2 = models.TextField(_("location_alpha2 ex: vn"), blank=True, null=True)
    location_name = models.TextField(_("location_name ex: Viet Nam"), blank=True, null=True)
    gpu_tflops = models.TextField(_("gpu_tflops"), blank=True, null=True)
    datacenter = models.TextField(
        _("datacenter, ex: datacenter/ miners/ consumerGpu"), blank=True, null=True
    )
    branch_name = models.TextField(_('branch_name'), null=True)
    batch_size = models.IntegerField(_('batch size'), default=8, help_text='Batch size', null=True)
    gpu_id = models.TextField(_('gpu_id'), null=True)
    serialno = models.TextField(_("serialno"), null=True)
    class MachineOptions(models.TextChoices):
        SECURE_CLOUD = "secure-cloud", _("secure-cloud")
        VM = "virtual-machines", _("virtual-machines")
        PM = "physical-machines", _("physical-machines")

    machine_options = models.CharField(
        _("machine_options"),
        max_length=64,
        choices=MachineOptions.choices,
        default=MachineOptions.VM,
        null=True,
    )
    created_at = models.DateTimeField(_('created at'), null=True, auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True)
    quantity_used = models.IntegerField(_('quantity has been used'),null=True, default=0)
    user_rented = models.IntegerField(_("number of user rented"), default=0, null=True)
    max_user_rental = models.IntegerField(
        _("Maximum number of user rentals"), default=1, null=True
    )
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        COMPLETED = 'completed', _('Completed')
        RENTING = 'renting', _('Renting')
        PENDING = 'pending', _('Pending')
        SUPPEND = "suppend", _("suppend")
        BEEN_REMOVED = "been_removed", _("been removed")
        IN_MARKETPLACE = 'in_marketplace', _('In Marketplace')
        UNDERPERFORMANCE = 'underperformance', _('Underperformance')
        FAILED = 'failed', _('Failed') # install failed

    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
        null=True
    )
    owner_id = models.IntegerField(_("owner_id"), null=True)
    gpus_machine = models.TextField(_("gpus_machine"), null=True)
    nvlink_bandwidth = models.TextField(_("nvlink_bandwidth"), null=True)
    def has_permission(self, user):
        return self

    def save(self, *args, **kwargs):
        # if not self.teraflops:
        #     self.teraflops = self.gpu_name
        super().save(*args, **kwargs)
    class Meta:
        db_table = 'compute_gpu'

class ComputeGpuPrice(models.Model):
    TYPE_CHOICES = (
        ('cpu', 'CPU'),
        ('gpu', 'GPU'),
        ('model', 'Model'),
        ('compute', 'Compute'),
    )
    id = models.AutoField(primary_key=True)
    compute_gpu_id = models.ForeignKey(
        ComputeGPU, to_field='id', on_delete=models.CASCADE,
        db_column='compute_gpu_id', related_name='prices', null=True
    )
    token_symbol = models.TextField()
    price = models.FloatField(default = 0)
    unit = models.CharField(_('unit '), max_length=20, default='hour')
    type =models.CharField(max_length=20, choices=TYPE_CHOICES, default='gpu')
    compute_marketplace_id = models.ForeignKey(
        ComputeMarketplace,
        to_field='id',
        on_delete=models.CASCADE,
        db_column='compute_marketplace_id',
        related_name='gpu_prices',
        null=True
    )
    model_marketplace_id = models.ForeignKey(
        ModelMarketplace,
        to_field='id',
        on_delete=models.CASCADE,
        db_column='model_marketplace_id',
        related_name='gpu_prices',
        null=True
    )
    class Meta:
        db_table = 'compute_gpu_price'

class ComputeTimeWorking(models.Model):
    id = models.AutoField(primary_key=True)
    compute_id = models.IntegerField(_('compute_id'), null=True)
    infrastructure_id = models.TextField(_('infrastructure_id'))
    time_start = models.CharField(_('time_start'), max_length=30)
    time_end = models.CharField(_('time_end'), max_length=30)
    
    day_range = models.JSONField(_('day_range'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True)
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        COMPLETED = 'completed', _('Completed')
        PENDING = 'pending', _('Pending')
        SUPPEND = 'suppend', _('Suppend')
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
        null=True
    )
    
    def has_permission(self, user):
        return self
    def set_day_range(self, start_day, end_day):
        self.day_range = {'start_day': start_day, 'end_day': end_day}

    def get_start_day(self):
        return self.day_range.get('start_day')

    def get_end_day(self):
        return self.day_range.get('end_day')
    class Meta:
        db_table = 'compute_timeworking'

class ComputeLogs(models.Model):
    id = models.AutoField(primary_key=True)
    compute_id = models.IntegerField(verbose_name='compute_id', null=True)
    model_id = models.IntegerField(verbose_name='model_id', null=True)
    ml_gpu_id = models.IntegerField(verbose_name='ml_gpu_id', null=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    log_message = models.TextField(_('log message'), null=True)
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_progress', _('In Progress')
        FAILED = 'failed', _('Failed')
        COMPLETED = 'completed', _('Completed')
    
    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
    )

    def __str__(self):
        return f"Compute: {self.compute.name}, Timestamp: {self.timestamp}"
    
    def has_permission(self, user):
        return self
    class Meta:
        db_table = 'compute_logs'

class History_Rent_Computes(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_rent_computes') 
    compute_marketplace = models.ForeignKey(ComputeMarketplace, related_name='history_rent_computes', on_delete=models.CASCADE, null=True)  
    compute_gpu = models.ForeignKey(ComputeGPU, related_name='history_rent_computes', on_delete=models.CASCADE, null=True)  
    time_start = models.DateTimeField(_('time_start'),auto_now_add=True)
    rental_hours = models.FloatField(_('rental_hours'), null=True)
    time_end = models.DateTimeField(_('time_end'), null=True)
    order_id = models.IntegerField(_('order_id'), null=True)
    date = models.DateTimeField( auto_now_add=True)
    mail_end_send = models.BooleanField(_('mail_end_send'), default=False, null=True)
    class Status(models.TextChoices):
        RENTING = 'renting', _('Renting')
        COMPLETED = 'completed', _('Completed')

    status = models.CharField(
        _('status'),
        max_length=64,
        choices=Status.choices,
        default=Status.RENTING,
        null=True
    )

    class Type(models.TextChoices):
        RENT_MARKETPLACE = "rent_marketplace", _("rent_marketplace")
        OWN_NOT_LEASING = "own_not_leasing", _("Own not leasing") # self host
        LEASING_OUT = "leasing_out", _("Leasing Out")

    type = models.CharField(
        _("type"),
        max_length=50,
        choices=Type.choices,
        default=Type.RENT_MARKETPLACE,
        null=True,
    )

    class InstallStatus(models.TextChoices):
        FAILED = 'failed', _('Failed')
        COMPLETED = "completed", _("Completed")
        INSTALLING = "installing", _("Installing")
        WAIT_VERIFY = "wait_verify", _("Wait verify")
        WAIT_CRYPTO = "wait_crypto", _("Wait crypto")

    compute_install = models.CharField(
        _('status'),
        max_length=64,
        choices=InstallStatus.choices,
        default=InstallStatus.COMPLETED,
        null=True
    )

    class SERVICE_TYPE(models.TextChoices):
        ALL_SERVICE = "full", _("ALl Service")
        STORAGE = "storage", _("Storage")
        MODEL_TRAINING = "model-training", _("Model Training")
        LABEL_TOOL = "label-tool", _("Labeling Tool")

    service_type = models.CharField(
        _("service_type"),
        max_length=64,
        choices=SERVICE_TYPE.choices,
        default=SERVICE_TYPE.ALL_SERVICE,
        null=True,
    )
    install_logs = models.TextField(_("install logs"), null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True)
    quantity_used = models.IntegerField(_("Quantity used card"),default=0, null=True)
    ip_address = models.TextField(_("ip address running"), null=True)
    port = models.TextField(_("port running"), null=True)
    schema = models.TextField(_("http, https"), null=True)
    container_network = models.TextField(_("container network"), null=True)
    class DELETED_BY(models.TextChoices):
        MANUAL_USER = "manual_user", _("manual user")
        AUTO_SERVICE = "auto_service", _("auto service")

    deleted_by = models.CharField(
        _("deleted_by"),
        max_length=64,
        choices=DELETED_BY.choices,
        default=None,
        null=True,
    )

    @property
    def notifications(self):
        return Notification.objects.filter(history_id=self.id)

    @property
    def new_notifications(self):
        return self.notifications.filter(is_read=False)

    def id(self):
        return id(self.id)

    def get_start_day(self):
        return self.day_range.get('start_day')

    def get_end_day(self):
        return self.day_range.get('end_day')

    def __init__(self, *args, **kwargs):
        super(History_Rent_Computes, self).__init__(*args, **kwargs)

    def has_permission(self, user):
        return self
    class Meta:
        db_table = 'history_rent_computes'

class Computes_Preference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='computes_preference') 
    price_from = models.FloatField(default = 0)
    price_to = models.FloatField(default = 0)
    unit = models.CharField(_('unit'), max_length=20, default='hour')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True)
    model_card = models.CharField(_('model_card'), max_length=300, default='gpu')

    def has_permission(self, user):
        return self

class Recommend_Price(models.Model):
    name = models.TextField(_('name'), default='')
    price_from = models.FloatField(default = 0)
    price_to = models.FloatField(default = 0)
    vram = models.TextField(_('vram'), blank=True, null=True)
    unit = models.CharField(_('unit'), max_length=20, default='hour')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), null=True, auto_now_add=True)
    type_card = models.TextField(_('type_card'), blank=True, null=True)
