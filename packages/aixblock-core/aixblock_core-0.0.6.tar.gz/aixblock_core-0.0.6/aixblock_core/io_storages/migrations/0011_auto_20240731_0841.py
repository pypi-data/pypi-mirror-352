from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('io_storages', '0010_auto_20221014_1708'),
    ]

    operations = [
        migrations.CreateModel(
            name='GDriverStorageMixin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bucket', models.TextField(blank=True, help_text='GDriver bucket name', null=True, verbose_name='bucket')),
                ('prefix', models.TextField(blank=True, help_text='GDriver bucket prefix', null=True, verbose_name='prefix')),
                ('regex_filter', models.TextField(blank=True, help_text='Cloud storage regex for filtering objects', null=True, verbose_name='regex_filter')),
                ('use_blob_urls', models.BooleanField(default=False, help_text='Interpret objects as BLOBs and generate URLs', verbose_name='use_blob_urls')),
                ('google_application_credentials', models.TextField(blank=True, help_text='The content of GOOGLE_APPLICATION_CREDENTIALS json file', null=True, verbose_name='google_application_credentials')),
            ],
            options={
                'abstract': False,
            },
        ),

        migrations.CreateModel(
            name='GDriverExportStorage',
            fields=[
                ('gdriverstoragemixin_ptr', models.OneToOneField(auto_created=True, on_delete=models.CASCADE, parent_link=True, primary_key=True, serialize=False, to='io_storages.gdriverstoragemixin')),
                ('title', models.CharField(blank=True, help_text='Cloud storage title', max_length=256, null=True, verbose_name='title')),
                ('description', models.TextField(blank=True, help_text='Cloud storage description', null=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Creation time', verbose_name='created at')),
                ('project',models.ForeignKey(help_text='A unique integer value identifying this project.', on_delete=django.db.models.deletion.CASCADE, related_name='io_storages_gdriverexportstorages', to='projects.project')),
                ('last_sync_count', models.PositiveIntegerField(blank=True, help_text='Count of tasks synced last time', null=True, verbose_name='last sync count')),
                ('last_sync', models.DateTimeField(blank=True, help_text='Last sync finished time', null=True, verbose_name='last sync')),
                ('can_delete_objects', models.BooleanField(blank=True, help_text='Deletion from storage enabled', null=True, verbose_name='can_delete_objects')),
                ('last_sync_job', models.CharField(blank=True, help_text='Last sync job ID', max_length=256, null=True, verbose_name='last_sync_job')),
            ],
            options={
                'abstract': False,
            },
            bases=('io_storages.gdriverstoragemixin', models.Model),
        ),

        migrations.CreateModel(
            name='GDriverImportStorage',
            fields=[
                ('gdriverstoragemixin_ptr', models.OneToOneField(auto_created=True, on_delete=models.CASCADE, parent_link=True, primary_key=True, serialize=False, to='io_storages.gdriverstoragemixin')),
                ('title', models.CharField(blank=True, help_text='Cloud storage title', max_length=256, null=True, verbose_name='title')),
                ('description', models.TextField(blank=True, help_text='Cloud storage description', null=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Creation time', verbose_name='created at')),
                ('presign', models.BooleanField(default=True, help_text='Generate presigned URLs', verbose_name='presign')),
                ('presign_ttl', models.PositiveSmallIntegerField(default=1, help_text='Presigned URLs TTL (in minutes)', verbose_name='presign_ttl')),
                ('project', models.ForeignKey(help_text='A unique integer value identifying this project.', on_delete=django.db.models.deletion.CASCADE, related_name='io_storages_gdriverexportstorages', to='projects.project')),
                ('last_sync_count', models.PositiveIntegerField(blank=True, help_text='Count of tasks synced last time', null=True, verbose_name='last sync count')),
                ('last_sync', models.DateTimeField(blank=True, help_text='Last sync finished time', null=True, verbose_name='last sync')),
                ('last_sync_job', models.CharField(blank=True, help_text='Last sync job ID', max_length=256, null=True, verbose_name='last_sync_job')),
            ],
            options={
                'abstract': False,
            },
            bases=('io_storages.gdriverstoragemixin', models.Model),
        ),

        migrations.CreateModel(
            name='GDriverImportStorageLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(help_text='External link key', verbose_name='key')),
                ('object_exists', models.BooleanField(default=True, help_text='Whether object under external link still exists', verbose_name='object exists')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Creation time', verbose_name='created at')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='io_storages_gdriverimportstoragelink', to='tasks.task')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='io_storages.gdriverimportstorage')),
            ],
            options={
                'abstract': False,
            },
        ),

        migrations.CreateModel(
            name='GDriverExportStorageLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_exists', models.BooleanField(default=True, help_text='Whether object under external link still exists', verbose_name='object exists')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Creation time', verbose_name='created at')),
                ('annotation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='io_storages_gdriverexportstoragelink', to='tasks.annotation')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='io_storages.gdriverexportstorage')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Update time', verbose_name='updated at'))
            ],
            options={
                'abstract': False,
            },
        ),
    ]
