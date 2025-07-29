from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("model_marketplace", "0014_update_field_history_model_rent"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelmarketplace",
            name="schema",
            field=models.TextField(("schema like: tcp, http, https, grpc"), null=True),
        )
    ]
