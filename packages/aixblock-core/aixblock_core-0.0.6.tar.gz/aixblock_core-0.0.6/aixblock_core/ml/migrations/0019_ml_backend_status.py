from django.db import migrations, models
import django.db.models.deletion
from django.utils.translation import gettext_lazy as _
from ..models import MLBackend

class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0018_add_type_training"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlbackend",
            name="install_status",
            field=models.CharField(
                _("install_status"),
                max_length=64,
                choices=MLBackend.INSTALL_STATUS.choices,
                default=MLBackend.INSTALL_STATUS.INSTALLING,
                null=True,
            ),
        )
    ]
