# Generated by Django 5.1.2 on 2024-11-19 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_jobreport_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='workflow_step',
            field=models.TextField(null=True),
        ),
    ]