from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0045_auto_20240607_2143"),
    ]

    operations = [
        migrations.AddField(
            model_name="computemarketplace",
            name="location_id",
            field=models.IntegerField(_("location_id"), blank=True, null=True),
        ),
        migrations.AddField(
            model_name="computemarketplace",
            name="location_alpha2",
            field=models.TextField(_("location_alpha2 ex: vn"), blank=True, null=True),
        ),
        migrations.AddField(
            model_name="computemarketplace",
            name="location_name",
            field=models.TextField(
                _("location_name ex: Viet Nam"), blank=True, null=True
            ),
        ),
    ]
