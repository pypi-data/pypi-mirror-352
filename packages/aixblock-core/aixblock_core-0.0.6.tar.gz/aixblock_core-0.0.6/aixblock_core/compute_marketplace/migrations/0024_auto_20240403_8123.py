from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0023_auto_20240402_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name="computegpu",
            name="power_consumption",
            field=models.TextField(('power_consumption'), blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="computegpu",
            name="memory_usage",
            field=models.TextField(('memory_usage'), blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="computegpu",
            name="power_usage",
            field=models.TextField(('power_usage'), blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="computegpu",
            name="gpu_memory",
            field=models.TextField(('gpu_memory'), blank=True, null=True),
        ), 
        migrations.AlterField(
            model_name="Portfolio",
            name="token_name",
            field=models.CharField(max_length=100, default="United States Dollar")
        ),
       
    ]