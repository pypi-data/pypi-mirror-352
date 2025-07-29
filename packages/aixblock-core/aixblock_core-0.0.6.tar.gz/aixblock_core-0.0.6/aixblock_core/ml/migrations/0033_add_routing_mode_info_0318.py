from django.db import migrations, models

class Migration(migrations.Migration):
    
    dependencies = [
        ('ml', '0032_add_folder_run'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlbackend',
            name='routing_mode',
            field=models.CharField(
                verbose_name='routing_mode',
                max_length=64,
                choices=[
                    ('load_balance', 'load_balance'),
                    ('random', 'random'),
                    ('sequentially', 'sequentially')
                ],
                default='load_balance',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='mlbackend',
            name='cluster_mode',
            field=models.CharField(
                verbose_name='cluster_mode',
                max_length=64,
                choices=[
                    ('load_balance', 'load_balance'),
                    ('random', 'random'),
                    ('sequentially', 'sequentially')
                ],
                default='load_balance',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='mlbackend',
            name='routing_mode_status',
            field=models.BooleanField(
                verbose_name='routing_mode_status',
                default=True
            ),
        ),
        migrations.AddField(
            model_name='mlbackend',
            name='order',
            field=models.IntegerField(
                verbose_name='order',
                blank=True,
                default=0,
                null=True
            ),
        ),
    ]
