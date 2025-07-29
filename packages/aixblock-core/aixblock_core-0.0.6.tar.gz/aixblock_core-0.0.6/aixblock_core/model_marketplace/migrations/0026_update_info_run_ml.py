from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0025_dataset_storage_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelmarketplace",
            name="info_run",
            field=models.JSONField(("info run"), null=True, blank=True)
        )
    ]
