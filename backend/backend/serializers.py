from backend.models import Pipeline, PipelineRun, JobReport, Subworkflow
from rest_framework import serializers


class PipelineSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Pipeline
        fields = [
            "slug",
            "description",
            "tools",
            "owner",
            "version",
        ]


class PipelineRunSerializer(serializers.ModelSerializer):
    job_reports_count = serializers.SerializerMethodField()
    started_by = serializers.ReadOnlyField(source="started_by.username")

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
            "job_reports_count",
        ]

    def get_job_reports_count(self, obj):
        return obj.job_reports_count


class JobReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReport
        fields = ["name", "output", "run"]
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
        ]
