# Generated by Django 4.2.16 on 2024-10-29 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_alter_pipelinerun_output_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelinerun',
            name='user',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
