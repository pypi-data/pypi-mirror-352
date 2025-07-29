from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reward_point', '0002_auto_20242603_1441'), 
    ]

    operations = [
        migrations.RenameField(
            model_name='Action_Point',
            old_name='date',
            new_name='date_start',
        ),
        migrations.AddField(
            model_name='Action_Point',
            name='date_end',
            field=models.DateField(null=True),
        ),
    ]
