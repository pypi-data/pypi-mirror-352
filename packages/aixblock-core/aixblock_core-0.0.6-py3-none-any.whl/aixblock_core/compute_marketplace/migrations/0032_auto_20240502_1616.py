from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0031_auto_20240430_0945'),
    ]

    operations = [
    migrations.AlterField(
        model_name='computes_preference',
        name='model_card',
        field=models.CharField(max_length=300, verbose_name='model_card', default='gpu'),
    ),
]
