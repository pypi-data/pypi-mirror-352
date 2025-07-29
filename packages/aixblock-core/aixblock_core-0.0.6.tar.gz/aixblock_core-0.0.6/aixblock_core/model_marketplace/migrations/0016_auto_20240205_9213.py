from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0015_add_schema_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="History_Rent_Model",
            name="model_new_id",
            field=models.TextField(("model_new_id"), default="0"),
        )
    ]
