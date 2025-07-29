from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0049_history_compute_install_error"),
    ]

    operations = [
        migrations.AlterField(
            model_name="computemarketplace",
            name="config",
            field=models.JSONField(_("config"), null=True, blank=True),
        ),
    ]
