from django.db import migrations, models
from ..models import ModelMarketplace
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0017_add_model_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelmarketplace",
            name="model_id",
            field=models.TextField(_("model source id"), null=True),
        ),
        migrations.AddField(
            model_name="modelmarketplace",
            name="model_token",
            field=models.TextField(_("model source token"), null=True),
        ),
        migrations.AlterField(
            model_name="modelmarketplace",
            name="checkpoint_id",
            field=models.TextField(_("checkpoint id"), null=True),
        ),
        migrations.AddField(
            model_name="modelmarketplace",
            name="checkpoint_token",
            field=models.TextField(_("checkpoint token"), null=True),
        ),
        migrations.AddField(
            model_name="modelmarketplace",
            name="checkpoint_source",
            field=models.TextField(
                _("checkpoint_source"),
                choices=ModelMarketplace.CheckpointSource.choices,
                default=ModelMarketplace.CheckpointSource.ROBOFLOW,
            ),
        ),
        migrations.AddField(
            model_name="modelmarketplace",
            name="model_source",
            field=models.TextField(
                _("model_source"),
                choices=ModelMarketplace.ModelSource.choices,
                default=ModelMarketplace.ModelSource.DOCKER_HUB,
            ),
        ),
    ]
