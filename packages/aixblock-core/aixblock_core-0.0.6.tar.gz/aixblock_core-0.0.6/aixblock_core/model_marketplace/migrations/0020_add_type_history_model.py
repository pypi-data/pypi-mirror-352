from django.db import migrations, models
from ..models import History_Rent_Model
from django.utils.translation import gettext_lazy as _

class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0019_add_filename"),
    ]

    operations = [
        migrations.AddField(
            model_name="History_Rent_Model",
            name="type",
            field=models.CharField(
                _("type"),
                max_length=64,
                choices=History_Rent_Model.TYPE.choices,
                default=History_Rent_Model.TYPE.RENT,
                null=True,
                blank=True,
            ),
        )
    ]
