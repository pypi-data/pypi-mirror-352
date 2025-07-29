from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0023_history_build_and_deploy_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkpointmodelmarketplace',
            name='ml_id',
            field=models.IntegerField(null=True, verbose_name='ml id'),
        ),
        migrations.AlterField(
            model_name='checkpointmodelmarketplace',
            name='catalog_id',
            field=models.IntegerField(null=True, verbose_name='catalog id'),
        ),
    ]
