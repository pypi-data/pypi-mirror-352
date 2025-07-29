from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("compute_marketplace", "0053_update_project_compute"),
    ]

    operations = [
        migrations.AlterField(
            model_name='computemarketplace',
            name='type',
            field=models.TextField(
                choices=[
                    ('MODEL-SYSTEM', 'MODEL-SYSTEM'),
                    ('MODEL-CUSTOMER', 'MODEL-CUSTOMER'),
                    ('MODEL-PROVIDER-VAST', 'MODEL-PROVIDER-VAST'),
                    ('MODEL-PROVIDER-EXABIT', 'MODEL-PROVIDER-EXABIT')
                ],
                default='MODEL-CUSTOMER',
                verbose_name='type'
            ),
        ),
    ]
