from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('io_storages', '0011_auto_20240731_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='s3importstorage',
            name='export_storage',
            field=models.IntegerField(null=True, blank=True, verbose_name='export_storage'),
        )
    ]
