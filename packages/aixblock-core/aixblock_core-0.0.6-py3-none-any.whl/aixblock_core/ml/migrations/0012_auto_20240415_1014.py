from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0011_auto_20240408_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlgpu',
            name='port',
            field=models.IntegerField(null=True),
        )       
    ]