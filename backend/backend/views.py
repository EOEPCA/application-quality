from . import serializers
from backend.models import Pipeline, PipelineRun, JobReport, Subworkflow
from backend.tasks import run_workflow_task
from backend.utils.opensearch import index_pipeline_job_report

from django.utils import timezone
from jinja2 import Template

from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

import logging
import yaml

logger = logging.getLogger(__name__)


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = serializers.PipelineSerializer
    lookup_field = "slug"


class PipelineRunViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PipelineRunSerializer
    lookup_field = "id"

    def get_queryset(self):
        slug = self.kwargs["pipeline_slug"]
        if slug == "_":
            return PipelineRun.objects.all()
        return PipelineRun.objects.filter(pipeline_id=slug)

    def create(self, request, *args, **kwargs):
        slug = self.kwargs["pipeline_slug"]
        logger.info(f"Creating a new run for pipeline '{slug}'")

        try:
            pipeline = Pipeline.objects.get(slug=slug)
        except Pipeline.DoesNotExist:
            logger.warning(f"Couldn't create a new run: Pipeline {slug} not found")
            return Response(
                {"error": "Pipeline not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        pipeline_run = PipelineRun.objects.create(
            pipeline=pipeline,
            usage_report="",
            start_time=timezone.now(),
            status="starting",
            user=request.user.username if request.user.is_authenticated else None,
        )
        logger.info(f"Pipeline run created with id {pipeline_run.id}")

        yaml_cwl = self.render_cwl(pipeline)
        cwl = yaml.safe_load(yaml_cwl)

        logger.info(f"Running workflow with id {pipeline_run.id}")
        run_workflow_task.delay(
            run_id=pipeline_run.id,
            repo_url=request.data.get("repo_url"),
            repo_branch=request.data.get("repo_branch", "main"),
            slug=slug,
            cwl=cwl,
        )

        pipeline_run.executed_cwl = yaml_cwl
        pipeline_run.inputs = {
            "pipeline_id": slug,
            "run_id": str(pipeline_run.id),
            "repo_url": request.data.get("repo_url"),
            "repo_branch": request.data.get("repo_branch"),
        }
        pipeline_run.save()
        logger.debug(f"Run {pipeline_run.id} updated with CWL and inputs")

        serializer = self.get_serializer(pipeline_run)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def render_cwl(self, pipeline):
        logger.debug(f"Rendering CWL for pipeline '{pipeline.slug}'")
        rendered_subworkflows = []

        for subworkflow in pipeline.tools.all():
            logger.debug(f"Rendering subworkflow '{subworkflow}'")
            subtemplate = Template(subworkflow.definition)
            subcontext = {"tools": list(subworkflow.tools.all())}
            subtool = {
                "pipeline_step": subworkflow.pipeline_step,
                "definition": subtemplate.render(subcontext),
            }
            rendered_subworkflows.append(subtool)

        template = Template(pipeline.template)
        context = {"subworkflows": rendered_subworkflows}
        result = template.render(context)
        logger.debug(f"CWL rendered for pipeline '{pipeline.slug}'")
        return result


class JobReportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.JobReportSerializer

    def get_queryset(self):
        slug = self.kwargs["pipeline_slug"]
        run_id = self.kwargs["run_id"]
        queryset = JobReport.objects.filter(run__pipeline__slug=slug, run_id=run_id)

        tool_name = self.request.query_params.get("name")
        if tool_name:
            queryset = queryset.filter(name=tool_name)

        return queryset

    def create(self, request, *args, **kwargs):
        slug = self.kwargs["pipeline_slug"]
        run_id = self.kwargs["run_id"]
        logger.info(f"Creating a new job report for '{slug}' pipeline, run_id {run_id}")

        tool_name = request.query_params.get("name")
        if not tool_name:
            raise ValidationError("Tool 'name' is required as a query parameter.")

        try:
            run = PipelineRun.objects.get(pipeline__slug=slug, id=run_id)
        except PipelineRun.DoesNotExist:
            logger.warning(f"Couln't create a job report: Run {run_id} for pipeline '{slug}' not found")
            return Response(
                {"error": "Pipeline run not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if JobReport.objects.filter(run=run, name=tool_name).exists():
            logger.warning(f"Couln't create a job report: A job report for '{tool_name}' already exists in run {run_id}")
            return Response(
                {"error": f"A job report for '{tool_name}' already exists for this run."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job_report = JobReport.objects.create(
            name=tool_name,
            run=run,
            output=request.data,
            created_at=timezone.now()
        )

        index_pipeline_job_report(job_report)
        logger.info(f"Job report created for tool '{tool_name}' in run {run_id}")

        serializer = self.get_serializer(job_report)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class SubworkflowViewSet(viewsets.ModelViewSet):
    queryset = Subworkflow.objects.all()
    serializer_class = serializers.SubworkflowSerializer
    lookup_field = "slug"
