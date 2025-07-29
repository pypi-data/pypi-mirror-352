from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0052_update_scale"),
    ]

    operations = [
        migrations.AddField(
            model_name="computemarketplace",
            name="project_id",
            field=models.IntegerField(_("project_id"), null=True),
        ),
    ]
