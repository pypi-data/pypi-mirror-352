from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0036_remove_field_renter_id_compute_gpu"),
    ]

    operations = [
        migrations.AlterField(
            model_name='computemarketplace',
            name='type',
            field=models.TextField(
                choices=[
                    ('MODEL-SYSTEM', 'MODEL-SYSTEM'),
                    ('MODEL-CUSTOMER', 'MODEL-CUSTOMER'),
                    ('PROVIDER-VAST', 'MODEL-PROVIDER-VAST')
                ],
                default='MODEL-CUSTOMER',
                verbose_name='type'
            ),
        ),
    ]
