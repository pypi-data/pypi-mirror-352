from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0022_auto_20240401_7129'),
        ('auth', '0001_initial'),  
    ]

    operations = [
        migrations.CreateModel(
            name='History_Rent_Computes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('renting', 'Renting'), ('completed', 'Completed')], default='renting', max_length=64, null=True, verbose_name='status')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_rent_computes', to='users.User')),
                ('compute_marketplace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_rent_computes', to='compute_marketplace.ComputeMarketplace')),
                ('compute_gpu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_rent_computes', to='compute_marketplace.ComputeGPU')),
            ],
            options={
                'db_table': 'history_rent_computes',
            },
        ),
    ]