# Generated by Django 4.2.16 on 2024-10-23 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True)),
                ('definition', models.TextField()),
                ('version', models.CharField(default='0.0', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PipelineRun',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True)),
                ('cwl', models.TextField()),
                ('usage_report', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('completion_time', models.DateTimeField()),
                ('status', models.CharField(max_length=100)),
                ('user', models.CharField(max_length=100, unique=True)),
                ('output', models.TextField()),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='runs', to='backend.pipeline')),
            ],
        ),
        migrations.CreateModel(
            name='PipelineRunJobReport',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('content', models.TextField(default='{}')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='backend.pipelinerun')),
            ],
        ),
    ]
