from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0013_auto_20240123_0617'), 
    ]

    operations = [
        migrations.CreateModel(
            name='Action_Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('date', models.DateField(null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('activity', models.CharField(max_length=255)),
                ('point', models.IntegerField(default=0)),
                ('detail', models.TextField(blank=True, null=True)),
                ('customer', models.TextField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User_Action_History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_action_history', to='reward_point.Action_Point')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_action_history', to='orders.Order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_action_history',to='users.User')),
            ],
        ),
        migrations.CreateModel(
            name='User_Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_point', to='users.User')),
            ],
        ),
    ]
