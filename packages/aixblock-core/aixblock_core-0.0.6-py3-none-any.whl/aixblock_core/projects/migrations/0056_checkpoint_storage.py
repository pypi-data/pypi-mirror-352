from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0055_project_auto_train_format"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="checkpoint_storage",
            field=models.CharField(_('trained checkpoint storage'), max_length=30, null=True, default=None, blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="checkpoint_storage_huggingface",
            field=models.CharField(_('hugging face token'), max_length=100, null=True, default=None, blank=True),
        ),
    ]
