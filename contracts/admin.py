from django.contrib import admin

from .models import ScheduleMetadata


@admin.register(ScheduleMetadata)
class ScheduleMetadataAdmin(admin.ModelAdmin):
    pass
