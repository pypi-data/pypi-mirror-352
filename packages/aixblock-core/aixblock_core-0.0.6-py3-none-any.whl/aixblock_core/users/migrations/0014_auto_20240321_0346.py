from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0013_auto_20240123_0617'), 
    ]

    operations = [
        migrations.CreateModel(
            name='Rank_Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('minimum_points', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='rank_point',
            field=models.ForeignKey(null=True, on_delete=models.SET_NULL, to='users.Rank_Point'),
        ),
       
    ]
