from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0050_update_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="history_rent_computes",
            name="mail_end_send",
            field=models.BooleanField(
                _("mail_end_send"),
                default=False,
                null=True,
            ),
        ),
    ]
