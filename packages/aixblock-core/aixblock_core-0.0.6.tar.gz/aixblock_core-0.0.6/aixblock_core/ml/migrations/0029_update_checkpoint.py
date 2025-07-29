from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0028_update_mlbackend"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlnetworkhistory",
            name="checkpoint_id",
            field=models.IntegerField(('checkpoint_id'), null=True)
        ),
    ]
