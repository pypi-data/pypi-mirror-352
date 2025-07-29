from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0014_auto_20240321_0346'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=True, help_text='Designates whether to treat this user as a verified.',
                                      verbose_name='is verified'),
        ),
    ]
