from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'job_name', 'state', 'job_type', 'starting_date', 'end_date', 'completion_time')
    list_filter = ('state', 'job_type')
    search_fields = ('job_id', 'job_name')
    date_hierarchy = 'starting_date'