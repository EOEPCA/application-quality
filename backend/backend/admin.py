from backend import models

from django.contrib import admin
from django.db.models import JSONField
# https://django-svelte-jsoneditor.readthedocs.io/en/latest/index.html
# Customised using SVELTE_JSONEDITOR_PROPS in the Django settings
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget



class PipelineSettings(admin.ModelAdmin):
    list_display = ("name", "description", "owner", "version", "created_at", "edited_at")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

class PipelineRunSettings(admin.ModelAdmin):
    list_display = ("__str__", "pipeline", "start_time", "completion_time", "status", "user", "started_by")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

class ToolSettings(admin.ModelAdmin):
    list_display = ("slug", "name", "version", "status", "available")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

class CommandSettings(admin.ModelAdmin):
    list_display = ("slug", "name", "version")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

class JobReportSettings(admin.ModelAdmin):
    list_display = ("__str__", "name", "created_at")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

admin.site.register(models.Pipeline, PipelineSettings)
admin.site.register(models.PipelineRun, PipelineRunSettings)
admin.site.register(models.Subworkflow, ToolSettings)
admin.site.register(models.CommandLineTool, CommandSettings)
admin.site.register(models.JobReport, JobReportSettings)
admin.site.register(models.Tag)
