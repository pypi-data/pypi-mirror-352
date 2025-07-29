from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0021_model_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="CheckpointModelMarketplace",
            name="checkpoint_storage_name",
            field=models.TextField(("checkpoint storage name"), null=True),
        )
    ]
