from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0021_auto_20240329_1821'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComputeLogs',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('compute_id', models.IntegerField(verbose_name='compute_id', null=True)),
                ('model_id', models.IntegerField(verbose_name='model_id', null=True)),
                ('ml_gpu_id', models.IntegerField(verbose_name='ml_gpu_id', null=True)),
                ('timestamp', models.DateTimeField(verbose_name='timestamp', auto_now_add=True)),
                ('log_message', models.TextField(verbose_name='log message', null=True)),
                ('status', models.CharField(
                    verbose_name='status',
                    max_length=64,
                    choices=[
                        ('created', 'Created'),
                        ('in_progress', 'In Progress'),
                        ('failed', 'Failed'),
                        ('completed', 'Completed'),
                    ],
                    default='created',
                )),
            ],
            options={
                'db_table': 'compute_logs',
            },
        ),
    ]