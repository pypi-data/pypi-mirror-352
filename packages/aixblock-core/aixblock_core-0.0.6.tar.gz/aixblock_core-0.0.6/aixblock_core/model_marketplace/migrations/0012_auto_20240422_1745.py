from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_marketplace', '0011_auto_20240329_0611'),
    ]

    operations = [
        migrations.AddField(
            model_name='ModelMarketplace',
            name='download_count',
            field=models.IntegerField(verbose_name='download count', default=0),
        ),
        
        migrations.AddField(
            model_name='ModelMarketplace',
            name='like_count',
            field=models.IntegerField(verbose_name='like count', default=0),
        ),

        migrations.CreateModel(
            name='History_Rent_Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_id', models.IntegerField(default=0, verbose_name='model_id')),
                ('model_new_id', models.IntegerField(default=0, verbose_name='model_new_id')),
                ('project_id', models.IntegerField(default=0, verbose_name='project_id')),
                ('user_id', models.IntegerField(default=0, verbose_name='user_id')),
                ('model_usage', models.IntegerField(default=5, verbose_name='model_usage')),
                ('time_start', models.CharField(max_length=30, verbose_name='time_start')),
                ('time_end', models.CharField(max_length=30, verbose_name='time_end')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='updated at')),
                ('status', models.CharField(choices=[('renting', 'Renting'), ('completed', 'Completed')], default='renting', max_length=64, null=True, verbose_name='status')),
            ],
            options={
                'db_table': 'history_rent_model',
            },
        ),
    ]
