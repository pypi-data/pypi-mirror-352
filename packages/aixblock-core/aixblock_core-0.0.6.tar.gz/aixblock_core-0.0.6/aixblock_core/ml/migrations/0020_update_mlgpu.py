from django.db import migrations, models
import django.db.models.deletion
from django.utils.translation import gettext_lazy as _
from ..models import MLGPU


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0019_ml_backend_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mlgpu",
            name="model_install",
            field=models.CharField(
                _("model_install"),
                max_length=64,
                choices=MLGPU.InstallStatus.choices,
                default=MLGPU.InstallStatus.INSTALLING,
                null=True,
            ),
        )
    ]
