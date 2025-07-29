from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0014_add_deleted_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlgpu",
            name="model_history_rent_id",
            field=models.IntegerField(("model_history_rent_id"), default=0, null=True),
        ),
    ]
