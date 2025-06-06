# Generated by Django 5.1.4 on 2025-03-12 10:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommandLineTool',
            fields=[
                ('slug', models.SlugField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('definition', models.TextField()),
                ('version', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True)),
                ('template', models.TextField()),
                ('version', models.CharField(max_length=50, null=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pipelines', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PipelineRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usage_report', models.JSONField(blank=True)),
                ('start_time', models.DateTimeField(blank=True)),
                ('completion_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100)),
                ('user', models.CharField(blank=True, max_length=100, null=True)),
                ('inputs', models.JSONField(blank=True, null=True)),
                ('output', models.JSONField(blank=True, null=True)),
                ('executed_cwl', models.TextField(blank=True, null=True)),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='runs', to='backend.pipeline')),
                ('started_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pipeline_runs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField()),
                ('output', models.JSONField()),
                ('created_at', models.DateTimeField(null=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobreports', to='backend.pipelinerun')),
            ],
        ),
        migrations.CreateModel(
            name='Subworkflow',
            fields=[
                ('slug', models.SlugField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True)),
                ('pipeline_step', models.TextField()),
                ('definition', models.TextField()),
                ('user_params', models.JSONField(default=dict)),
                ('version', models.CharField(max_length=50)),
                ('tools', models.ManyToManyField(related_name='subworkflows', to='backend.commandlinetool')),
                ('tags', models.ManyToManyField(blank=True, related_name='subworkflows', to='backend.tag')),
            ],
        ),
        migrations.AddField(
            model_name='pipeline',
            name='tools',
            field=models.ManyToManyField(blank=True, to='backend.subworkflow'),
        ),
        migrations.AddConstraint(
            model_name='pipeline',
            constraint=models.UniqueConstraint(fields=('name', 'owner', 'version'), name='unique_name_owner_version'),
        ),
    ]
