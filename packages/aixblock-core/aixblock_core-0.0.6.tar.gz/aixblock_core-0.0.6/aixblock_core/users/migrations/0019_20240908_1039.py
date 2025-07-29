from django.db import migrations, models
import django.db.models.deletion
from ..models import Notification


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0018_20240808_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.CharField(
                max_length=64,
                choices=Notification.Status.choices,
                default=Notification.Status.Info,
                null=True,
                verbose_name='status'
            ),
        ),
    ]
