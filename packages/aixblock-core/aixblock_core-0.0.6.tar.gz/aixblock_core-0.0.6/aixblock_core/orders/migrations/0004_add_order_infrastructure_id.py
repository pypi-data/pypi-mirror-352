from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_add_order_compute_gpu'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInfrastructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('infrastructure_id', models.CharField(max_length=100)),
                ('order', models.ForeignKey(on_delete=models.CASCADE, related_name='order', to='orders.Order')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='orderinfrastructure',
            unique_together={('order', 'infrastructure_id')},
        ),
    ]