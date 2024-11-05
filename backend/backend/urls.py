from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from backend import views

urlpatterns = [
	path("pipelines/", views.PipelineList.as_view()),
	path("pipelines/<str:slug>/", views.PipelineDetail.as_view()),
	path("pipelines/<str:slug>/runs/", views.PipelineRunList.as_view()),
	path("pipelines/<str:slug>/runs/<int:id>/", views.PipelineRunDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
