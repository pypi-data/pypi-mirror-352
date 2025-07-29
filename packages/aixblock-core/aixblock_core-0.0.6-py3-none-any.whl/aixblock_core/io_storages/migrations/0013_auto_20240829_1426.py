from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('io_storages', '0012_auto_20240826_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='azureblobimportstorage',
            name='export_storage',
            field=models.IntegerField(null=True, blank=True, verbose_name='export_storage'),
        ),
        migrations.AddField(
            model_name='gcsimportstorage',
            name='export_storage',
            field=models.IntegerField(null=True, blank=True, verbose_name='export_storage'),
        ),
        migrations.AddField(
            model_name='redisimportstorage',
            name='export_storage',
            field=models.IntegerField(null=True, blank=True, verbose_name='export_storage'),
        ),
        migrations.AddField(
            model_name='gdriverimportstorage',
            name='export_storage',
            field=models.IntegerField(null=True, blank=True, verbose_name='export_storage'),
        )
    ]
    
