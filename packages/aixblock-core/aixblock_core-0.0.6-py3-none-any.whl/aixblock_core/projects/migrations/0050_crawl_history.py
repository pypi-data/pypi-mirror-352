from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0049_ml_config"),
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_id', models.TextField(default=None, verbose_name='search_id')),
                ('keyword', models.TextField(default=None, verbose_name='keyword')),
                ('type', models.TextField(default=None, verbose_name='keyword')),  # Should this be 'type' instead of 'keyword'?
                ('quantity', models.TextField(default=None, verbose_name='quantity')),
                ('is_search_all', models.BooleanField(default=False, verbose_name='is_search_all')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deleted at')),
                ('project', models.ForeignKey(
                    to='projects.Project',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='projects',
                    null=True
                )),
            ],
        ),
    ]
