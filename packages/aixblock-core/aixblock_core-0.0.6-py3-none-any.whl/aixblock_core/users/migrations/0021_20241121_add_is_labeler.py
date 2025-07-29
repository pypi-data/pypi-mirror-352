from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_20240908_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_labeler',
            field=models.BooleanField(default=False, null=False),
        ),
    ]
