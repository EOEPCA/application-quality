from backend.models import Pipeline, PipelineRun, JobReport, Subworkflow
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class PipelineSerializer(ModelSerializer):
    class Meta:
        model = Pipeline
        fields = "__all__"


class PipelineRunSerializer(ModelSerializer):
    job_reports_count = SerializerMethodField()

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
            "job_reports_count",
        ]

    def get_job_reports_count(self, obj):
        return obj.job_reports_count


class JobReportSerializer(ModelSerializer):
    class Meta:
        model = JobReport
        fields = ["name", "output", "run"]
        read_only_fields = ["run"]


# class ToolSerializer(ModelSerializer):
#     class Meta:
#         model = Tool
#         fields = "__all__"


class SubworkflowSerializer(ModelSerializer):
    class Meta:
        model = Subworkflow
        fields = "__all__"
