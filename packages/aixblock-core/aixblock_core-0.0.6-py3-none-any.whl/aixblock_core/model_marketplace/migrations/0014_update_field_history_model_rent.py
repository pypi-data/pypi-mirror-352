from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0013_merge_0012_add_key_field_0012_auto_20240422_1745"),
    ]

    operations = [
        migrations.AlterField(
            model_name="History_Rent_Model",
            name="time_start",
            field=models.DateTimeField(("time_start"), auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="History_Rent_Model",
            name="time_end",
            field=models.DateTimeField(("time_end"), null=True),
        ),
        migrations.AddField(
            model_name="History_Rent_Model",
            name="deleted_at",
            field=models.DateTimeField(("deleted at"), null=True),
        ),
    ]
