from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0024_auto_20240403_8123'),
    ]

    operations = [
        migrations.AlterField(
            model_name="History_Rent_Computes",
            name="compute_gpu",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_rent_computes', to='compute_marketplace.ComputeGPU', null=True)
        ),
    ]