from rest_framework.routers import DefaultRouter
from backend.views import (
    PipelineViewSet,
    PipelineRunViewSet,
    PipelineRunJobReportViewSet,
    ToolViewSet,
)

router = DefaultRouter()

router.register(r"pipelines", PipelineViewSet, basename="pipeline")
router.register(
    r"pipelines/(?P<pipeline_slug>[^/.]+)/runs",
    PipelineRunViewSet,
    basename="pipeline-run",
)
router.register(
    r"pipelines/(?P<pipeline_slug>[^/.]+)/runs/(?P<run_id>[^/.]+)/jobreport",
    PipelineRunJobReportViewSet,
    basename="pipeline-run-jobreport",
)
router.register(r"tool", ToolViewSet, basename="tool")

urlpatterns = router.urls
