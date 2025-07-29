from django.contrib import admin
from projects.models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'num_tasks', 'need_to_qa', 'need_to_qc', 'is_draft', 'is_published', 'created_by', 'created_at']
    list_filter = ['is_draft', 'is_published']
    search_fields = ['title', 'description']
    ordering = ['created_at']
    fieldsets = [
        ('General', {'fields': ('title', 'description', 'organization', 'created_by', 'is_draft', 'is_published', 'need_to_qa', 'need_to_qc')}),
        ('Config', {'fields': ('label_config', 'epochs', 'batch_size', 'image_width', 'image_height')}),
    ]