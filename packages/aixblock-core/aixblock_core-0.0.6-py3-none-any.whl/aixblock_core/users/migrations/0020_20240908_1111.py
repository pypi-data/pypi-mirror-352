from django.db import migrations, models

import uuid

def update_uuids(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.filter(uuid__isnull=True):
        user.uuid = uuid.uuid4()
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_20240908_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.TextField(default=None, unique=True, verbose_name='UUID', null=True, blank=True, editable=False),
        ),
        migrations.RunPython(update_uuids),
    ]
