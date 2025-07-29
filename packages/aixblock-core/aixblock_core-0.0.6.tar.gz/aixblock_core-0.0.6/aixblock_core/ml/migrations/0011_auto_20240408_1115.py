from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0010_auto_20240402_8712'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlbackend',
            name='ram',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),

        migrations.CreateModel(
            name='MLLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='timestamp', auto_now_add=True)),
                ('log_message', models.TextField(verbose_name='log message', null=True)),
                ('ml_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ml.MLBackend')),
                ('ml_gpu', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ml.MLGPU')),
            ],
        ),
       
    ]