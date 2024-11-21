from django.db import models


class Pipeline(models.Model):
    slug            = models.SlugField(primary_key=True, max_length=50, unique=True)
    description     = models.TextField(null=True)
    template        = models.TextField()
    tools           = models.ManyToManyField("CommandLineTool") # -> Subworkflow (Change variable if problematic)
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

    @property
    def job_reports_count(self):
        return self.jobreports.count()

    def __str__(self):
        return f"{'✅' if self.status == 'succeeded' else '❌'} Run {self.id}: {self.pipeline.slug}"


class JobReport(models.Model):
    run             = models.ForeignKey(PipelineRun, related_name="jobreports", on_delete=models.CASCADE)
    name            = models.SlugField(max_length=50)
    output          = models.TextField()
    created_at      = models.DateTimeField(null=True)

    def __str__(self):
        return f"Run {self.run.id} ({self.run.pipeline.slug}): {self.name} job"


class Tag(models.Model):
    name            = models.CharField(max_length=50, unique=True) # primary_key

    def __str__(self):
        return self.name


# class Tool(models.Model): # Delete and make 2 classes: Subworkflow and CommandLineTool
#     slug            = models.SlugField(primary_key=True, max_length=50, unique=True) # Both
#     name            = models.CharField(max_length=50) # Both
#     description     = models.TextField(null=True) # Subworkflow
#     workflow_step   = models.TextField(blank=True) # Subworkflow
#     definition      = models.TextField() # Both
#     tags            = models.ManyToManyField(Tag, related_name="tools") # Subworkflow
#     is_cwl          = models.BooleanField() # None
#     tools           = models.ManyToManyField("self", symmetrical=False, blank=True) # Subworkflow -> CLT
#     version         = models.CharField(max_length=50, null=True) # Both

#     def __str__(self):
#         return self.name


class Subworkflow(models.Model):
    slug            = models.SlugField(primary_key=True, max_length=50)
    name            = models.CharField(max_length=50)
    description     = models.TextField(null=True)
    pipeline_step   = models.TextField(blank=True)
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
