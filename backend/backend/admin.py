from django.contrib import admin
from backend import models

class PipelineSettings(admin.ModelAdmin):
    list_display = ("name", "description", "owner", "version", "created_at", "edited_at")

class PipelineRunSettings(admin.ModelAdmin):
    list_display = ("__str__", "pipeline", "start_time", "completion_time", "status", "user", "started_by")

class ToolSettings(admin.ModelAdmin):
    list_display = ("slug", "name", "version")

class CommandSettings(admin.ModelAdmin):
    list_display = ("slug", "name", "version")

class JobReportSettings(admin.ModelAdmin):
    list_display = ("__str__", "name", "created_at")

admin.site.register(models.Pipeline, PipelineSettings)
admin.site.register(models.PipelineRun, PipelineRunSettings)
admin.site.register(models.Subworkflow, ToolSettings)
admin.site.register(models.CommandLineTool, CommandSettings)
admin.site.register(models.JobReport, JobReportSettings)
admin.site.register(models.Tag)
