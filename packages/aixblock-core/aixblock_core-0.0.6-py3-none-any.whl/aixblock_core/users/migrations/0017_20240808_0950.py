from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0016_20240808_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.TextField(verbose_name='type', null=True),
        ),
    ]
