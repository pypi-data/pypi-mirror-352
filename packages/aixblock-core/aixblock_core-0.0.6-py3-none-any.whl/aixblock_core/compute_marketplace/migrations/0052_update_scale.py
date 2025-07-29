from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0051_update_mail_send"),
    ]

    operations = [
        migrations.AddField(
            model_name="computemarketplace",
            name="is_scale",
            field=models.BooleanField(_("is_scale"), default=False, null=True),
        ),
    ]
