from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0008_auto_20240622_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization_project_permission',
            name='is_labeler',
            field=models.BooleanField(default=False, null=True, verbose_name='is labeler'),
        ),
        migrations.AddField(
            model_name='organization_project_permission',
            name='is_qa',
            field=models.BooleanField(default=False, null=True, verbose_name='is QA'),
        ),
        migrations.AddField(
            model_name='organization_project_permission',
            name='is_qc',
            field=models.BooleanField(default=False, null=True, verbose_name='is QC'),
        ),
    ]
