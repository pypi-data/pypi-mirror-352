from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0012_auto_20240415_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlbackend',
            name='deleted_at',
            field=models.DateTimeField(('deleted at'), null=True)
        )       
    ]