from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0010_auto_20240312_1726'),  
    ]

    operations = [
        migrations.AddField(
            model_name='computegpuprice',
            name='compute_marketplace_id',
            field=models.IntegerField(default=0, verbose_name='compute_marketplace_id', null=True),
        ),
        migrations.AddField(
            model_name='computegpuprice',
            name='model_marketplace_id',
            field=models.IntegerField(default=0, verbose_name='model_marketplace_id', null=True),
        ),
        migrations.AddField(
            model_name='computegpuprice',
            name='unit',
            field=models.CharField(
                verbose_name='unit',
                max_length=20,
                default='hour'
            ),
        ),
    ]
