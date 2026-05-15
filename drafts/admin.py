from django.contrib import admin

from .models import DraftSubmission


@admin.register(DraftSubmission)
class DraftSubmissionAdmin(admin.ModelAdmin):
    list_display = ['project', 'chapter', 'version', 'status', 'submitted_by', 'submitted_at']
    list_filter = ['chapter', 'status', 'submitted_at']
    search_fields = ['project__title', 'submitted_by__username', 'file_hash']
    autocomplete_fields = ['project', 'submitted_by']
