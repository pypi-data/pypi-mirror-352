from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0020_add_type_history_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelmarketplace",
            name="model_name",
            field=models.TextField(("model_name"), null=True),
        )
    ]
