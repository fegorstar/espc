# Generated by Django 5.0.7 on 2024-09-23 11:11

import cloudinary.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profile_picture', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('state', models.CharField(default='', max_length=250)),
                ('city', models.CharField(default='', max_length=250)),
                ('phone_number', models.CharField(max_length=11)),
                ('nin', models.CharField(blank=True, max_length=11, null=True, verbose_name='NIN')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
        ),
    ]
