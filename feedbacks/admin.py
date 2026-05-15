from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['draft', 'supervisor', 'decision', 'progress_score', 'created_at']
    list_filter = ['decision', 'created_at']
    search_fields = ['draft__project__title', 'supervisor__username', 'comments']
    autocomplete_fields = ['draft', 'supervisor']
