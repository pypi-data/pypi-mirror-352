from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0027_update_mlbackend"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlbackend",
            name="is_deploy",
            field=models.BooleanField(('is deploy'), default=False, null=True)
        ),
    ]
