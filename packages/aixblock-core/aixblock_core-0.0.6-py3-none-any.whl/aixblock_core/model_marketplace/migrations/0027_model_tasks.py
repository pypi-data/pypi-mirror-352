from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0026_update_info_run_ml"),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='name')),
                ('description', models.TextField(verbose_name='description', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='updated at')),
            ],
            options={
                'db_table': 'model_tasks',
            },
        ),
        migrations.AddField(
            model_name='ModelMarketplace',
            name='tasks',
            field=models.ManyToManyField(to='model_marketplace.ModelTask'),
        ),
    ]
