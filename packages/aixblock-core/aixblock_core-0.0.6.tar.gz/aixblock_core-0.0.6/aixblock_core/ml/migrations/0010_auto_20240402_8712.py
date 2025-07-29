from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0009_auto_20240401_9999'),
    ]

    operations = [
        migrations.AlterField(
        model_name='mlgpu',
        name='gpus_index',
        field=models.TextField(default='0', help_text='GPU_0,GPU_1,...', null=True, verbose_name='gpus_index'),
       ),
       
    ]