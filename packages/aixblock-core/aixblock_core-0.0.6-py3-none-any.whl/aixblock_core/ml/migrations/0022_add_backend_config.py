from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0021_auto_20240613_1231"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlbackend",
            name="entry_file",
            field=models.TextField(
                _('entry file'),
                blank=True,
                null=True,
                help_text='Entry file for training',
            ),
        ),
        migrations.AddField(
            model_name="mlbackend",
            name="arguments",
            field=models.JSONField(
                _('arguments'),
                blank=True,
                null=True,
                help_text='Arguments for training',
            ),
        ),
    ]
