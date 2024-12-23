from rest_framework.routers import DefaultRouter
from backend.views import (
    PipelineViewSet,
    PipelineRunViewSet,
    JobReportViewSet,
    SubworkflowViewSet,
)

router = DefaultRouter()

router.register(r"pipelines", PipelineViewSet, basename="pipeline")
router.register(
    r"pipelines/(?P<pipeline_slug>[^/.]+)/runs",
    PipelineRunViewSet,
    basename="pipeline-run",
)
router.register(
    r"pipelines/(?P<pipeline_slug>[^/.]+)/runs/(?P<run_id>[^/.]+)/jobreports",
    JobReportViewSet,
    basename="pipeline-run-jobreport",
)
router.register(r"tools", SubworkflowViewSet, basename="tool")

urlpatterns = router.urls
