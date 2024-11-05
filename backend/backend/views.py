from backend.models import Pipeline, PipelineRun
from backend.serializers import PipelineSerializer, PipelineRunSerializer
from django.utils import timezone
from jinja2 import Template
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response
from pycalrissian.run_workflow import run_workflow
import yaml


class PipelineList(ListCreateAPIView):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer


class PipelineDetail(RetrieveUpdateDestroyAPIView):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    lookup_field = "slug"


class PipelineRunList(ListCreateAPIView):
    serializer_class = PipelineRunSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        return PipelineRun.objects.filter(pipeline_id=slug)

    def create(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]

        try:
            pipeline = Pipeline.objects.get(slug=slug)
        except Pipeline.DoesNotExist:
            return Response(
                {"error": "Pipeline not found."}, status=status.HTTP_404_NOT_FOUND
            )

        pipeline_run = PipelineRun.objects.create(
            pipeline=pipeline,
            usage_report="",
            start_time=timezone.now(),
            completion_time=None,
            status="Starting",
            user=request.user.username if request.user.is_authenticated else None,
            output="",
        )

        template = Template(pipeline.template)
        context = {"tools": pipeline.tools.all()}
        cwl = yaml.safe_load(template.render(context))

        # try:
        workflow_output = run_workflow(
            repo_url=request.data.get("repo_url", ""),
            slug=slug,
            run_id=str(pipeline_run.id),
            cwl=cwl,
        )
        # except BaseException as e:
        #     raise e

        pipeline_run.usage_report = workflow_output.get(
            "usage_report", "Default usage report"
        )
        pipeline_run.completion_time = workflow_output.get(
            "completion_time", timezone.now()
        )
        pipeline_run.status = workflow_output.get("status", "active")
        # pipeline_run.executed_cwl = (
        #     yaml.dump(cwl, sort_keys=False)
        #     if pipeline_run.status == "succeeded"
        #     else None
        # )
        pipeline_run.output = workflow_output.get("output", "Workflow output details")
        pipeline_run.save()

        serializer = self.get_serializer(pipeline_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PipelineRunDetail(RetrieveAPIView):
    serializer_class = PipelineRunSerializer
    lookup_field = "id"

    def get_queryset(self):
        slug = self.kwargs["slug"]
        id = self.kwargs["id"]
        return PipelineRun.objects.filter(pipeline_id=slug, id=id)
