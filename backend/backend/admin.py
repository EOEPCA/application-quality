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

class TriggerTypeSettings(admin.ModelAdmin):
    list_display = ("__str__", "slug", "event_type_prefix", "status", "available")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

class TriggerSettings(admin.ModelAdmin):
    list_display = ("__str__", "owner", "trigger_type", "pipeline__name", "pipeline__version", "status", "enabled")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }

class TriggerEventSettings(admin.ModelAdmin):
    list_display = ("event_time", "trigger__trigger_type__name", "event_type", "source", "trigger__slug", "trigger__pipeline__name", "trigger__pipeline__version", "pipeline_run")
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget}
    }


admin.site.register(models.Pipeline, PipelineSettings)
admin.site.register(models.PipelineRun, PipelineRunSettings)
admin.site.register(models.Subworkflow, ToolSettings)
admin.site.register(models.CommandLineTool, CommandSettings)
admin.site.register(models.JobReport, JobReportSettings)
admin.site.register(models.TriggerType, TriggerTypeSettings)
admin.site.register(models.Trigger, TriggerSettings)
admin.site.register(models.TriggerEvent, TriggerEventSettings)
admin.site.register(models.Tag)
