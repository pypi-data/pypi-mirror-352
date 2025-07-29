"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data_manager', '0007_auto_20220708_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='View',
            name='is_private',
            field=models.BooleanField(verbose_name='private view', null=False, default=False),
        ),
    ]
