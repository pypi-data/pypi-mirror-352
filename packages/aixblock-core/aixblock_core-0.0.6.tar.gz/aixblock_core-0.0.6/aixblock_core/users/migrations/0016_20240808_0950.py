from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0015_20240520_add_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='detail',
            field=models.TextField(verbose_name='detail', null=True),
        ),

        migrations.AddField(
            model_name='notification',
            name='deleted_at',
            field=models.DateTimeField(verbose_name='deleted at', null=True),
        ),
    ]
