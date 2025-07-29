from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0037_auto_20240214_1254'), 
    ]

    operations = [
        # migrations.AddField(
        #     model_name='project',
        #     name='start_model_training',
        #     field=models.BooleanField(default=False, verbose_name='Start model training after any annotations are submitted or updated'),
        # ),
        # migrations.AddField(
        #     model_name='project',
        #     name='retrieve_predictions_automatically',
        #     field=models.BooleanField(default=False, verbose_name='Retrieve predictions when loading a task automatically'),
        # ),
        # migrations.AddField(
        #     model_name='project',
        #     name='show_predictions_to_annotators',
        #     field=models.BooleanField(default=False, verbose_name='Show predictions to annotators in the Label Stream and Quick View'),
        # ),
        migrations.AddField(
            model_name='project',
            name='steps_per_epochs',
            field=models.IntegerField(default=10, verbose_name='number steps per epochs', help_text='Number steps per epochs', null=True, blank=True),
        ),
    ]
