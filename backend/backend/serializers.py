from backend.models import Pipeline, PipelineRun, PipelineRunJobReport, Tool
from rest_framework.serializers import ModelSerializer


class PipelineSerializer(ModelSerializer):
    class Meta:
        model = Pipeline
        fields = "__all__"


class PipelineRunSerializer(ModelSerializer):
    class Meta:
        model = PipelineRun
        fields = "__all__"


class PipelineRunJobReportSerializer(ModelSerializer):
    class Meta:
        model = PipelineRunJobReport
        fields = ["name", "output", "run"]
        read_only_fields = ["run"]


class ToolSerializer(ModelSerializer):
    class Meta:
        model = Tool
        fields = "__all__"
