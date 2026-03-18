from rest_framework import serializers
from backend.models import Pipeline, PipelineRun, JobReport, Subworkflow, Tag, TriggerType, Trigger, TriggerEvent


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
            "owner",
            "owner_name",
            "created_at",
            "edited_at",
            "version",
        ]


class PipelineRunSerializer(serializers.ModelSerializer):
    job_reports_count = serializers.SerializerMethodField()
    started_by = serializers.ReadOnlyField(source="started_by.username")
    triggered_by = serializers.ReadOnlyField(source="triggered_by.id")

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
            "executed_cwl",
            "started_by",
            "triggered_by",
            "job_reports_count",
        ]

    def get_job_reports_count(self, obj):
        return obj.job_reports_count


class JobReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReport
        fields = ["id", "name", "instance", "created_at", "output", "run"]
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
    trigger_type = serializers.ReadOnlyField(source="trigger_type.slug")
    trigger_type_name = serializers.ReadOnlyField(source="trigger_type.name")
    pipeline_id = serializers.ReadOnlyField(source="pipeline.id")
    pipeline_name = serializers.ReadOnlyField(source="pipeline.name")
    pipeline_version = serializers.ReadOnlyField(source="pipeline.version")
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Trigger
        fields = ["slug", "owner", "description", "status", "cql2_filter", "params", "trigger_type", "trigger_type_name", "pipeline_id", "pipeline_name", "pipeline_version"]
        #read_only_fields = ["..."]


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
        fields = ["id", "source", "event_time", "event_type", "user", "trigger", "trigger_type", "trigger_type_name", "pipeline_run_id", "pipeline_id", "pipeline_name", "pipeline_version"]
        #read_only_fields = ["..."]