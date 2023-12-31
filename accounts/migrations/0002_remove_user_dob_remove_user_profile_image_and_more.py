# Generated by Django 4.2.3 on 2023-07-27 10:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='dob',
        ),
        migrations.RemoveField(
            model_name='user',
            name='profile_image',
        ),
        migrations.AddField(
            model_name='user',
            name='face_check',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='id_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='name_check',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='waddr_check',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='waddr_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.CreateModel(
            name='EmailActivation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('key', models.CharField(blank=True, max_length=50, null=True)),
                ('activated', models.BooleanField(default=False)),
                ('forced_expired', models.BooleanField(default=False)),
                ('expires', models.IntegerField(default=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
