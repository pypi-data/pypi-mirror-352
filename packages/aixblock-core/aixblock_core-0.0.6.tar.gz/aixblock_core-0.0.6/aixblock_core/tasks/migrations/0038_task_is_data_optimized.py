from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0037_task_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_data_optimized',
            field=models.BooleanField(blank=True, db_index=True, default=False, help_text='Mark optimization status of the task data', verbose_name='created by'),
        ),
    ]
