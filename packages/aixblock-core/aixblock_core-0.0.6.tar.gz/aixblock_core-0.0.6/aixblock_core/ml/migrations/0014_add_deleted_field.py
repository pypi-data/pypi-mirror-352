from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0013_auto_20240416_7213"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlgpu",
            name="deleted_at",
            field=models.DateTimeField(("deleted at"), null=True),
        ),
        migrations.AddField(
            model_name="mlbackendstatus",
            name="deleted_at",
            field=models.DateTimeField(("deleted at"), null=True),
        )
    ]
