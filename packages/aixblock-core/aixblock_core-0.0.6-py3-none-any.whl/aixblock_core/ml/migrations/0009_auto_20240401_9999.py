from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0008_auto_20240331_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlgpu',
            name='gpus_id',
            field=models.TextField(default='', help_text='1,2,3,4', verbose_name='gpus_id', null=True),
        ),
        migrations.AddField(
            model_name='mlgpu',
            name='compute_id',
            field=models.IntegerField(help_text='1', null=True, verbose_name='compute_id'),
        ),
    ]