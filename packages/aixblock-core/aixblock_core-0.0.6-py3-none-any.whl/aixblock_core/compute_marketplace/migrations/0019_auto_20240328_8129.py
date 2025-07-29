from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0018_auto_20240328_7123'),
    ]

    operations = [
        migrations.AddField(
            model_name='Trade',
            name='status',
            field=models.CharField(
                verbose_name='status',
                max_length=64,
                choices=[
                    ('renting', 'Renting'),
                    ('completed', 'Completed'),
                ],
                default='renting',
                null=True,
            ),
        ),
    ]
