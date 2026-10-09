from backend import models

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone
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


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "user", "expire_date", "is_active"]
    list_filter = ["expire_date"]
    search_fields = ["session_key"]
    readonly_fields = ["session_key", "expire_date", "decoded_data"]
    exclude = ["session_data"]
    ordering = ["-expire_date"]

    @admin.display(description="User")
    def user(self, obj):
        user_id = obj.get_decoded().get("_auth_user_id")
        if user_id is None:
            return "-"
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return f"(deleted user {user_id})"

    @admin.display(description="Active", boolean=True)
    def is_active(self, obj):
        return obj.expire_date > timezone.now()

    @admin.display(description="Decoded data")
    def decoded_data(self, obj):
        return obj.get_decoded()

    def has_add_permission(self, request):
        return False