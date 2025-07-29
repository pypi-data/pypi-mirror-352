from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import model_marketplace.models
import compute_marketplace.models

class Migration(migrations.Migration):

    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending', max_length=20)),
                ('unit', models.CharField(choices=[('USD', 'US Dollar'), ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('point', 'Reward Point')], default='USD', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('compute_marketplace', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='compute_marketplace.ComputeMarketplace')),
                ('model_marketplace', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='model_marketplace.ModelMarketplace')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
