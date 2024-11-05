from backend.models import Pipeline, PipelineRun
from rest_framework.serializers import ModelSerializer


class PipelineSerializer(ModelSerializer):
    class Meta:
        model = Pipeline
        fields = '__all__'


class PipelineRunSerializer(ModelSerializer):
    class Meta:
        model = PipelineRun
        fields = '__all__'
