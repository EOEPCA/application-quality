import logging
import os
import yaml

from django.utils import timezone
from django.db.utils import IntegrityError
from jinja2 import Template

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Pipeline, PipelineRun, JobReport, Subworkflow, Tag
from backend.tasks import run_workflow_task
from . import serializers


logger = logging.getLogger(__name__)

if os.getenv("OIDC_ENABLED", "false").lower() == "true":
    logger.info("OIDC is ENABLED")
else:
    logger.info("OIDC is DISABLED")

pipeline_cwl_template_path = os.path.join(os.path.dirname(__file__), "pipeline_template.cwl.jinja")

try:
    logger.info("Loading %s", pipeline_cwl_template_path)
    with open(pipeline_cwl_template_path, "r", encoding="utf-8") as file:
        pipeline_cwl_template = file.read()
except Exception as ex:
    logger.error("Error loading %s: %s", pipeline_cwl_template_path, str(ex))
    pipeline_cwl_template = f"Failed to load pipeline CWL template: {ex}"


class SettingsView(APIView):
    def get(self, request):
        settings_file = os.path.abspath("settings.yaml")
        try:
            logger.info("Loading %s", settings_file)
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = yaml.safe_load(f)
        except FileNotFoundError:
            logger.info("Not found: %s", settings_file)
            settings = None
        return Response(settings)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.owner == request.user


class PipelineViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PipelineSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Pipeline.objects.all()
        return (
            Pipeline.objects.filter(owner=self.request.user)
            | Pipeline.objects.filter(owner__isnull=True)
        )

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user, template=pipeline_cwl_template)
        except IntegrityError as ie:
            logger.error(ie)
            raise ValidationError(
                {
                    "detail": "A pipeline with this name, version, and owner already exists."
                }
            ) from ie

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return super().get_permissions()


class PipelineRunViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PipelineRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        logger.info("User %s is requesting pipeline runs (admin=%s)", user, user.is_staff)
        p_id = self.kwargs["pipeline_id"]
        if user.is_staff:
            if p_id == "_":
                return PipelineRun.objects
            return PipelineRun.objects.filter(pipeline_id=p_id)
        if p_id == "_":
            return PipelineRun.objects.filter(started_by=self.request.user)
        return PipelineRun.objects.filter(pipeline_id=p_id, started_by=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        logger.info("User %s is creating a pipeline run (admin=%s)", user, user.is_staff)
        pipeline_id = self.kwargs["pipeline_id"]
        logger.info("Creating a new run for pipeline %s", pipeline_id)

        try:
            pipeline = Pipeline.objects.get(id=pipeline_id)
        except Pipeline.DoesNotExist:
            logger.warning("Couldn't create a new run: Pipeline %s not found", pipeline_id)
            return Response(
                {"error": "Pipeline not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        pipeline_run = PipelineRun.objects.create(
            pipeline=pipeline,
            usage_report="",
            start_time=timezone.now(),
            status="starting",
            started_by=request.user,
        )
        logger.info("Pipeline run created with id %s", pipeline_run.id)

        yaml_cwl = self._render_cwl(pipeline)
        cwl = yaml.safe_load(yaml_cwl)

        logger.info("Running workflow with id %s", pipeline_run.id)
        payload = request.data  # dict
        run_workflow_task.delay(
            run_id=pipeline_run.id,
            parameters=payload.get("parameters"),
            cwl=cwl,
            username=request.user.username,
        )

        pipeline_run.executed_cwl = yaml_cwl
        pipeline_run.inputs = {
            "pipeline_id": pipeline_id,
            "run_id": str(pipeline_run.id),
        }
        pipeline_run.save()
        logger.debug("Run %s updated with CWL and inputs", pipeline_run.id)

        serializer = self.get_serializer(pipeline_run)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def _merge_params(self, subworkflow: Subworkflow, default_inputs: dict) -> dict:
        if subworkflow.slug not in default_inputs:
            return subworkflow.user_params

        merged_params = subworkflow.user_params.copy()
        defaults = default_inputs[subworkflow.slug]

        for key, value in merged_params.items():
            if isinstance(value, dict) and key in defaults:
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and "default" in sub_value:
                        if sub_key in defaults[key] and "default" in defaults[key][sub_key]:
                            merged_params[key][sub_key]["default"] = defaults[key][sub_key]["default"]

        return merged_params

    def _render_cwl(self, pipeline):
        logger.debug("Rendering CWL for pipeline '%s'", pipeline.id)
        rendered_subworkflows = []

        for subworkflow in pipeline.tools.all():
            logger.debug("Rendering subworkflow '%s'", subworkflow)
            subtemplate = Template(subworkflow.definition)
            subcontext = {"tools": list(subworkflow.tools.all())}
            subtool = {
                "definition": subtemplate.render(subcontext),
                "slug": subworkflow.pk,
                "user_params": self._merge_params(subworkflow, pipeline.default_inputs),
                "pipeline_step": subworkflow.pipeline_step,
            }
            rendered_subworkflows.append(subtool)

        template = Template(pipeline.template)
        context = {"subworkflows": rendered_subworkflows}
        result = template.render(context)
        logger.debug("CWL rendered for pipeline '%s'", pipeline.id)
        return result


class JobReportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.JobReportSerializer

    def get_queryset(self):
        pipeline_id = self.kwargs["pipeline_id"]
        run_id = self.kwargs["run_id"]
        queryset = JobReport.objects.filter(run__pipeline__id=pipeline_id, run_id=run_id)

        tool_name = self.request.query_params.get("name")
        if tool_name:
            queryset = queryset.filter(name=tool_name)
        instance = self.request.query_params.get("instance")
        if instance:
            queryset = queryset.filter(instance=instance)

        return queryset

    def create(self, request, *args, **kwargs):
        pipeline_id = self.kwargs["pipeline_id"]
        run_id = self.kwargs["run_id"]
        logger.info("Creating a new job report for pipeline %s, run_id %s", pipeline_id, run_id)

        tool_name = request.query_params.get("name")
        if not tool_name:
            raise ValidationError("Tool 'name' is required as a query parameter.")
        
        # The (optional) instance parameter allows to distinguish reports from scattered steps
        instance = request.query_params.get("instance", "")

        try:
            run = PipelineRun.objects.get(pipeline__id=pipeline_id, id=run_id)
        except PipelineRun.DoesNotExist:
            logger.warning(
                "Couln't create a job report: Run %s for pipeline %s not found",
                run_id,
                pipeline_id
            )
            return Response(
                {"error": "Pipeline run not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if JobReport.objects.filter(run=run, name=tool_name, instance=instance).exists():
            logger.warning(
                "Could not create a job report: A job report for '%s'/'%s' already exists in run %s",
                tool_name,
                instance,
                run_id
            )
            return Response(
                {"error": f"A job report for '{tool_name}/{instance}' already exists for this run."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job_report = JobReport.objects.create(
            name=tool_name,
            instance=instance,
            run=run,
            output=request.data,
            created_at=timezone.now()
        )

        logger.info("Job report created for tool '%s'/'%s' in run %s", tool_name, instance, run_id)

        serializer = self.get_serializer(job_report)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class SubworkflowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subworkflow.objects.all()
    serializer_class = serializers.SubworkflowSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer