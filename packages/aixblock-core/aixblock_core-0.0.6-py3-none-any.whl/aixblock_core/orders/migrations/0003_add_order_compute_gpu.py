# your_app_name/migrations/0003_auto_add_ordercomputegpu.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_auto_20240401_8123"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderComputeGPU",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="orders.Order",
                    ),
                ),
                (
                    "compute_gpu",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="compute_marketplace.ComputeGPU",
                    ),
                ),
            ],
            options={
                "unique_together": {("order", "compute_gpu")},
            },
        ),
        migrations.AddField(
            model_name="order",
            name="compute_gpus",
            field=models.ManyToManyField(
                related_name="orders",
                through="orders.OrderComputeGPU",
                to="compute_marketplace.ComputeGPU",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="service_fee",
            field=models.CharField(max_length=100, null=True)
        ),
    ]
