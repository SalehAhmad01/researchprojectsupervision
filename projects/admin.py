from django.contrib import admin

from .models import ResearchProject, SupervisorAssignment


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'supervisor', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'deadline']
    search_fields = ['title', 'abstract', 'student__username', 'supervisor__username']
    autocomplete_fields = ['student', 'supervisor', 'coordinator']


@admin.register(SupervisorAssignment)
class SupervisorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'supervisor', 'assigned_by', 'assigned_at']
    autocomplete_fields = ['project', 'supervisor', 'assigned_by']
