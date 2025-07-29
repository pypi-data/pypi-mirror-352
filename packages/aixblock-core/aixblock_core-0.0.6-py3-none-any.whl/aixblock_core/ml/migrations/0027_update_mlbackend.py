from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0026_update_ml_network"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlbackend",
            name="mlnetwork",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ml_backends",
                to="ml.MLNetwork",
                null=True,
                blank=True,
            ),
        ),
    ]
