from backend.models import Pipeline, PipelineRun, PipelineRunJobReport, Tool
from backend.serializers import (
    PipelineSerializer,
    PipelineRunSerializer,
    PipelineRunJobReportSerializer,
    ToolSerializer,
)
from django.utils import timezone
from jinja2 import Template
from pycalrissian.run_workflow import run_workflow
from rest_framework import status

# from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import yaml


class PipelineViewSet(ModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    lookup_field = "slug"


class PipelineRunViewSet(ModelViewSet):
    serializer_class = PipelineRunSerializer
    lookup_field = "id"

    def get_queryset(self):
        slug = self.kwargs["pipeline_slug"]
        return PipelineRun.objects.filter(pipeline_id=slug)

    def create(self, request, *args, **kwargs):
        slug = self.kwargs["pipeline_slug"]

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


class PipelineRunJobReportViewSet(ModelViewSet):
    queryset = PipelineRunJobReport.objects.all()
    serializer_class = PipelineRunJobReportSerializer

    def get_queryset(self):
        pipeline_slug = self.kwargs["pipeline_slug"]
        run_id = self.kwargs["run_id"]
        return PipelineRunJobReport.objects.filter(run__pipeline__slug=pipeline_slug, run_id=run_id)

    def create(self, request, *args, **kwargs):
        pipeline_slug = self.kwargs["pipeline_slug"]
        run_id = self.kwargs["run_id"]

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                pipeline = Pipeline.objects.get(slug=pipeline_slug)
                pipeline_run = PipelineRun.objects.get(id=run_id, pipeline=pipeline)
            except Pipeline.DoesNotExist:
                return Response({"error": "Pipeline not found."}, status=status.HTTP_404_NOT_FOUND)
            except PipelineRun.DoesNotExist:
                return Response({"error": "PipelineRun not found."}, status=status.HTTP_404_NOT_FOUND)

            job_report, created = PipelineRunJobReport.objects.update_or_create(
                name=serializer.validated_data['name'],
                run=pipeline_run,
                defaults={"output": serializer.validated_data['output']}
            )

            message = "Job report created successfully" if created else "Job report updated successfully"
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ToolViewSet(ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    lookup_field = "slug"
