from django.urls import path
from rest_framework.routers import DefaultRouter
from backend.views import (
    PipelineViewSet,
    PipelineRunViewSet,
    JobReportViewSet,
    SubworkflowViewSet,
    TagViewSet,
    TriggerTypeViewSet,
    TriggerViewSet,
    TriggerEventViewSet,
    TriggerRunViewSet,
    SettingsView,
    ActionsView,
    EventsView,
)

router = DefaultRouter()

router.register(r"pipelines",                                                            PipelineViewSet,     basename="pipeline")
router.register(r"pipelines/(?P<pipeline_id>[^/.]+)/runs",                               PipelineRunViewSet,  basename="pipeline-run")
router.register(r"pipelines/(?P<pipeline_id>[^/.]+)/runs/(?P<run_id>[^/.]+)/jobreports", JobReportViewSet,    basename="pipeline-run-jobreport")
router.register(r"tools",                                                                SubworkflowViewSet,  basename="tool")
router.register(r"tags",                                                                 TagViewSet,          basename="tag")
router.register(r"triggertypes",                                                         TriggerTypeViewSet,  basename="trigger-type")
router.register(r"triggers",                                                             TriggerViewSet,      basename="trigger")
router.register(r"triggers/(?P<trigger_id>[^/.]+)/events",                               TriggerEventViewSet, basename="trigger-event")
router.register(r"triggers/(?P<trigger_id>[^/.]+)/runs",                                 TriggerRunViewSet,   basename="trigger-run")

urlpatterns = router.urls

urlpatterns += [
    path("settings/", SettingsView.as_view(), name="settings"),
    path("actions/<slug:action_name>", ActionsView.as_view(), name="actions"),
    path("events/", EventsView.as_view(), name="events"),
]
