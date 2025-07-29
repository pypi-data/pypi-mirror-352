from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0046_add_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="computemarketplace",
            name="username",
            field=models.TextField(
                _("storage user name"), blank=True, null=True, editable=False
            ),
        ),
        migrations.AddField(
            model_name="computemarketplace",
            name="password",
            field=models.TextField(
                _("storage password"), blank=True, null=True, editable=False
            ),
        ),
        migrations.AddField(
            model_name="computemarketplace",
            name="api_port",
            field= models.TextField(_("api port"), null=True)
        ),

    ]
