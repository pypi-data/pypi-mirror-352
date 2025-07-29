from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0028_add_filed_history_rent_compute'),
    ]

    operations = [
        migrations.CreateModel(
            name='Computes_Preference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_from', models.FloatField(default=0)),
                ('price_to', models.FloatField(default=0)),
                ('unit', models.CharField(default='hour', max_length=20, verbose_name=('unit'))),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=('created at'))),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name=('updated at'))),
                ('deleted_at', models.DateTimeField(null=True, verbose_name=('deleted at'))),
                ('model_card', models.CharField(default='hour', max_length=20, verbose_name=('model_card'))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='computes_preference', to='users.User')),
            ],
        ),
    ]
