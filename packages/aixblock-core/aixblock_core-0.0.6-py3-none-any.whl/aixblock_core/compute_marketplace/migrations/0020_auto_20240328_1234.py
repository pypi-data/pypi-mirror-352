from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0019_auto_20240328_8129'),
    ]

    operations = [
        migrations.AddField(
            model_name='computemarketplace',
            name='is_using_cpu',
            field=models.BooleanField(('is_using_cpu'),default=False, null=True)
        ),
    ]
