from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InstallationService",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("version", models.TextField(max_length=10, null=True)),
                ("image", models.TextField(null=True)),
                ("registry", models.TextField(null=True)),
                (
                    "environment",
                    models.CharField(
                        choices=[
                            ("prod", "Production"),
                            ("dev", "Development"),
                            ("stg", "Staging"),
                        ],
                        default="dev",
                        max_length=64,
                        verbose_name="environment",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "active"),
                            ("inactive", "inactive"),
                            ("error", "error"),
                        ],
                        default="active",
                        max_length=64,
                        verbose_name="status",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="updated at"
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(null=True, verbose_name="deleted at"),
                ),
            ],
        ),
    ]
