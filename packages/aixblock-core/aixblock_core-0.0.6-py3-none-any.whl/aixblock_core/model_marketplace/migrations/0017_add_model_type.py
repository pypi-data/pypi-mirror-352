from django.db import migrations, models
from ..models import ModelMarketplace

class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0016_auto_20240205_9213"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelmarketplace",
            name="model_type",
            field=models.CharField(
                ("model_type"),
                max_length=64,
                choices=ModelMarketplace.ModelType.choices,
                default=ModelMarketplace.ModelType.RENT_MARKETPLACE,
                null=True,
            ),
        )
    ]
