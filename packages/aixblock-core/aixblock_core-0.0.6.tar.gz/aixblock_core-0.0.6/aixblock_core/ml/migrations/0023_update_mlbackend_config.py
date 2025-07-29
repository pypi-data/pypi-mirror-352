from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0022_add_backend_config"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mlbackend",
            name="entry_file",
        ),
        migrations.RemoveField(
            model_name="mlbackend",
            name="arguments",
        ),
        migrations.AddField(
            model_name="mlbackend",
            name="config",
            field=models.JSONField(
                _("config"),
                blank=True,
                null=True,
                help_text="config for ml train, predict, dashboard ",
            ),
        ),
    ]
