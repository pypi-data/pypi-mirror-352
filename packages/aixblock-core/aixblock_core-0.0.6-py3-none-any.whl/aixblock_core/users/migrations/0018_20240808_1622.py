from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0017_20240808_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='history_id',
            field=models.IntegerField(null=True, verbose_name='history_id'),
        ),
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.CharField(
                max_length=64,
                choices=[
                    ('info', 'Info'),
                    ('sucessful', 'Sucessful'),
                    ('danger', 'Danger'),
                    ('warning', 'Warning'),
                    ('default', 'Default')
                ],
                default='info',
                null=True,
                verbose_name='status'
            ),
        ),
    ]
