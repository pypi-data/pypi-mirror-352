from django.db import migrations, models
from ..models import ModelMarketplace
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0018_mode_marketplace"),
    ]

    operations = [
        migrations.AddField(
            model_name="CheckpointModelMarketplace",
            name="file_name",
            field=models.TextField(_("file_name"), null=True),
        ),
    ]