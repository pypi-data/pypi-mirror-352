from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reward_point', '0001_initial'), 
    ]

    operations = [
        migrations.AddField(
            model_name='user_action_history',
            name='created_by',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='user_action_history',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
    ]
