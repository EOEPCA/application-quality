from django.db import models
from django.contrib.auth.models import User


class Pipeline(models.Model):
    slug            = models.SlugField(primary_key=True, max_length=50, unique=True)
    description     = models.TextField(null=True)
    template        = models.TextField()
    tools           = models.ManyToManyField("Subworkflow", blank=True)
    owner           = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="pipelines")
    version         = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.slug


class PipelineRun(models.Model):
    pipeline        = models.ForeignKey(Pipeline, related_name="runs", on_delete=models.CASCADE)
    usage_report    = models.JSONField(blank=True)
    start_time      = models.DateTimeField(blank=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    status          = models.CharField(max_length=100, blank=True)
    user            = models.CharField(max_length=100, blank=True, null=True)
    inputs          = models.JSONField(blank=True, null=True)
    output          = models.JSONField(blank=True, null=True)
    executed_cwl    = models.TextField(blank=True, null=True)
    started_by      = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="pipeline_runs")

    @property
    def job_reports_count(self):
        return self.jobreports.count()

    def __str__(self):
        return f"{'✅' if self.status == 'succeeded' else '❌'} Run {self.id}: {self.pipeline.slug}"


class JobReport(models.Model):
    run             = models.ForeignKey(PipelineRun, related_name="jobreports", on_delete=models.CASCADE)
    name            = models.SlugField(max_length=50)
    output          = models.JSONField()
    created_at      = models.DateTimeField(null=True)

    def __str__(self):
        return f"Run {self.run.id} ({self.run.pipeline.slug}): {self.name} job"


class Tag(models.Model):
    name            = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Subworkflow(models.Model):
    slug            = models.SlugField(primary_key=True, max_length=50)
    name            = models.CharField(max_length=50)
    description     = models.TextField(null=True)
    pipeline_step   = models.TextField()
    definition      = models.TextField()
    tags            = models.ManyToManyField(Tag, related_name="subworkflows", blank=True)
    tools           = models.ManyToManyField("CommandLineTool", related_name="subworkflows")
    version         = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CommandLineTool(models.Model):
    slug            = models.SlugField(primary_key=True, max_length=50)
    name            = models.CharField(max_length=50)
    definition      = models.TextField()
    version         = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name
