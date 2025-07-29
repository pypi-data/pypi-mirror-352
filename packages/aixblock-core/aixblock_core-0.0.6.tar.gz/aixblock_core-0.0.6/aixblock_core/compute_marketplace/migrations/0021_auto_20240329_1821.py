from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0020_auto_20240328_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='computegpu',
            name='batch_size',
            field=models.IntegerField(('batch size'), default=8, help_text='Batch size', null=True)
        ),
    ]