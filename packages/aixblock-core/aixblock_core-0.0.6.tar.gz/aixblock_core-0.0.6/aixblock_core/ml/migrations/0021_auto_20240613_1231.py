from django.db import migrations, models
import django.db.models.deletion
from django.utils.translation import gettext_lazy as _
from ..models import  MLBackendState


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0020_update_mlgpu"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mlbackend",
            name="state",
            field=models.CharField(
                max_length=3,
                choices=MLBackendState.choices,
                default=MLBackendState.DISCONNECTED,
            ),
        )
    ]
