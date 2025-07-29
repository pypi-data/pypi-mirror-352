from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0054_update_provider_exabit"),
    ]

    operations = [
        migrations.AddField(
            model_name="trade",
            name="wallet_address",
            field=models.CharField(max_length=500, null=True)
        ),
    ]
