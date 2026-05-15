from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'department', 'is_active', 'is_verified']
    list_filter = ['role', 'department', 'is_active', 'is_verified']
    fieldsets = UserAdmin.fieldsets + (
        ('Research Supervision Profile', {'fields': ('role', 'department', 'student_id', 'staff_id', 'phone', 'is_verified')}),
    )
