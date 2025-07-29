from django.contrib import admin
from tasks.models import Task, Annotation


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'is_labeled', 'comment_count', 'updated_by', 'created_at', 'updated_at']
    list_filter = ['is_labeled', 'project', 'updated_by']
    ordering = ['created_at']
    fieldsets = [
        (None, {'fields': ('project', 'data', 'file_upload')}),
    ]

    def has_add_permission(self, request):
        return False


@admin.register(Annotation)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'completed_by', 'created_at']
    list_filter = ['completed_by']
    ordering = ['created_at']
    fieldsets = [
        (None, {'fields': ('task', 'result', 'completed_by')}),
    ]

    def has_add_permission(self, request):
        return False
