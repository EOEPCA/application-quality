from django.urls import path
from rest_framework.routers import DefaultRouter
from backend.views import (
    PipelineViewSet,
    PipelineRunViewSet,
    JobReportViewSet,
    SubworkflowViewSet,
    TagViewSet,
    SettingsView
)

router = DefaultRouter()

router.register(r"pipelines",                                                               PipelineViewSet,    basename="pipeline")
router.register(r"pipelines/(?P<pipeline_id>[^/.]+)/runs",                                  PipelineRunViewSet, basename="pipeline-run")
router.register(r"pipelines/(?P<pipeline_id>[^/.]+)/runs/(?P<run_id>[^/.]+)/jobreports",    JobReportViewSet,   basename="pipeline-run-jobreport")
router.register(r"tools",                                                                   SubworkflowViewSet, basename="tool")
router.register(r"tags",                                                                    TagViewSet,         basename="tag")
router.register(r"pipelines",                                                               PipelineViewSet,    basename="pipeline")
router.register(r"pipelines/(?P<pipeline_id>[^/.]+)/runs",                                  PipelineRunViewSet, basename="pipeline-run")
router.register(r"pipelines/(?P<pipeline_id>[^/.]+)/runs/(?P<run_id>[^/.]+)/jobreports",    JobReportViewSet,   basename="pipeline-run-jobreport")
router.register(r"tools",                                                                   SubworkflowViewSet, basename="tool")
router.register(r"tags",                                                                    TagViewSet,         basename="tag")

urlpatterns = router.urls

urlpatterns += [
    path("settings/", SettingsView.as_view(), name="settings"),
]
