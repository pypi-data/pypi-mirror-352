from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0024_update_filed_ml"),
    ]

    operations = [
        migrations.AddField(
            model_name="DatasetModelMarketplace",
            name="dataset_storage_name",
            field=models.TextField(("dataset storage name"), null=True),
        )
    ]
