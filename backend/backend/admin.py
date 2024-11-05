from django.contrib import admin
from backend import models

admin.site.register(models.Pipeline)
admin.site.register(models.PipelineRun)
admin.site.register(models.PipelineRunJobReport)
admin.site.register(models.Tool)
admin.site.register(models.Tag)
