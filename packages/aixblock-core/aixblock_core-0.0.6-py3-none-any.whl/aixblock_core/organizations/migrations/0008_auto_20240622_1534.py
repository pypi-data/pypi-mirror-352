from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_auto_20250605_2224'),
        ('users', '0001_initial'),  # Đảm bảo rằng bạn có migration cho ứng dụng 'users'
    ]

    operations = [
        migrations.AddField(
            model_name='organization_project_permission',
            name='user',
            field=models.ForeignKey(
                to='users.User',
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='organization_project',
                null=True,
                verbose_name='created_by'
            ),
        ),
    ]
