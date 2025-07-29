from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_add_order_infrastructure_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payer_email',
            field=models.CharField(max_length=100, null=False, default=""),
        ),
        migrations.AddField(
            model_name='order',
            name='payer_full_name',
            field=models.CharField(max_length=100, null=False, default=""),
        ),
    ]
