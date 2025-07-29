from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0038_project_add_fields'), 
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='max_parked_tasks',
            field=models.IntegerField(('maximum parked tasks'), default=1,
                                            help_text='Maximum number of parked tasks per user', null=False)
        ),
    ]
