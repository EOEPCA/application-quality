# Generated by Django 5.1.4 on 2025-03-27 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipeline',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='edited_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
