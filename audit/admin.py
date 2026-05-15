from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'path', 'method', 'ip_address', 'created_at']
    list_filter = ['action', 'method', 'created_at']
    search_fields = ['actor__username', 'action', 'path', 'user_agent']
    readonly_fields = ['actor', 'action', 'object_type', 'object_id', 'path', 'method', 'ip_address', 'user_agent', 'created_at']
