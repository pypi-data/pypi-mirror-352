from django.db import migrations, models
from ..models import ModelMarketplace


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0022_checkpoint_storage_name"),
    ]

    operations = [
        migrations.CreateModel(
            name='History_Build_And_Deploy_Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.TextField(null=True, verbose_name='version')),
                ('model_id', models.IntegerField(null=True, verbose_name='model_id')),
                ('checkpoint_id', models.IntegerField(null=True, verbose_name='checkpoint_id')),
                ('dataset_id', models.IntegerField(null=True, verbose_name='dataset_id')),
                ('project_id', models.IntegerField(null=True, verbose_name='project_id')),
                ('user_id', models.IntegerField(null=True, verbose_name='user_id')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(null=True, auto_now_add=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deleted at')),
                ('type', models.CharField(
                    max_length=64, 
                    choices=[
                        ('build', 'build model'), 
                        ('deploy', 'deploy model')
                    ], 
                    default='build', 
                    null=True, 
                    blank=True, 
                    verbose_name='type'
                )),
            ],
        ),
    ]
