from rest_framework import serializers
from django.contrib.auth.models import User

from backend.models import (
    Pipeline,
    PipelineRun,
    JobReport,
    Subworkflow,
    Tag,
    TriggerType,
    Trigger,
    TriggerEvent,
)


class UserMinifiedSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "full_name")

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.username


class PipelineSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Pipeline
        fields = [
            "id",
            "name",
            "description",
            "tools",
            "default_inputs",
            "quality_rules",
            "owner",
            "owner_name",
            "created_at",
            "edited_at",
            "version",
        ]


class PipelineRunSerializer(serializers.ModelSerializer):
    digest_quality = serializers.SerializerMethodField()
    started_by = serializers.ReadOnlyField(source="started_by.username")
    trigger_event = serializers.SerializerMethodField()
    job_reports_count = serializers.SerializerMethodField()

    class Meta:
        model = PipelineRun
        fields = [
            "id",
            "pipeline",
            "usage_report",
            "start_time",
            "completion_time",
            "status",
            "user",
            "inputs",
            "output",
            "digest",
            "digest_quality",
            "executed_cwl",
            "started_by",
            "trigger_event",
            "job_reports_count",
        ]

    def get_job_reports_count(self, obj):
        return obj.job_reports_count

    def get_digest_quality(self, obj):
        return obj.digest_quality

    def get_trigger_event(self, obj):
        # Fetch the first trigger event from the relation if it exists
        first_event = obj.triggered_by.first()
        return first_event.id if first_event else None


class JobReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReport
        fields = ["id", "name", "instance", "created_at", "output", "digest", "run"]
        read_only_fields = ["run"]


class SubworkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subworkflow
        fields = [
            "slug",
            "name",
            "description",
            "user_params",
            "tags",
            "tools",
            "version",
            "status",
            "available",
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TriggerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerType
        fields = ["slug", "name", "description", "status", "data"]


class TriggerSerializer(serializers.ModelSerializer):
    trigger_type = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=TriggerType.objects.all()
    )
    trigger_type_name = serializers.ReadOnlyField(source="trigger_type.name")
    pipeline_id = serializers.PrimaryKeyRelatedField(
        source="pipeline", 
        queryset=Pipeline.objects.all()
    )
    pipeline_name = serializers.ReadOnlyField(source="pipeline.name")
    pipeline_version = serializers.ReadOnlyField(source="pipeline.version")
    owner = UserMinifiedSerializer(read_only=True)
    owner_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    event_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trigger
        fields = [
            "slug",
            "owner",
            "owner_name",
            "description",
            "enabled",
            "status",
            "cql2_filter",
            "params_default",
            "params_mapping",
            "trigger_type",
            "trigger_type_name",
            "pipeline_id",
            "pipeline_name",
            "pipeline_version",
            "event_count",
        ]

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        # If present, replace the "owner_name" with the corresponding User instance
        owner_name = internal_value.pop("owner_name", None)
        if owner_name:
            try:
                user_instance = User.objects.get(username=owner_name)
                internal_value["owner"] = user_instance
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "owner": [f"User '{owner_name}' does not exist."],
                })
        return internal_value


class TriggerEventSerializer(serializers.ModelSerializer):
    trigger = serializers.ReadOnlyField(source="trigger.slug")
    trigger_type = serializers.ReadOnlyField(source="trigger.trigger_type.slug")
    trigger_type_name = serializers.ReadOnlyField(source="trigger.trigger_type.name")
    pipeline_run_id = serializers.ReadOnlyField(source="pipeline_run.id")
    pipeline_id = serializers.ReadOnlyField(source="pipeline_run.pipeline.id")
    pipeline_name = serializers.ReadOnlyField(source="pipeline_run.pipeline.name")
    pipeline_version = serializers.ReadOnlyField(source="pipeline_run.pipeline.version")
    user = serializers.ReadOnlyField(source="pipeline_run.user.username")

    class Meta:
        model = TriggerEvent
        fields = [
            "id",
            "source",
            "event_time",
            "event_type",
            "event_headers",
            "event_body",
            "user",
            "trigger",
            "trigger_type",
            "trigger_type_name",
            "pipeline_run_id",
            "pipeline_id",
            "pipeline_name",
            "pipeline_version",
        ]
