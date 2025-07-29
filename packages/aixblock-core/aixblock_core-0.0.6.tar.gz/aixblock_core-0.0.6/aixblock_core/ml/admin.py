from django.contrib import admin
from ml.models import MLBackend, MLBackendTrainJob


@admin.register(MLBackend)
class MLBackendAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'title', 'url', 'description', 'created_at', 'updated_at']
    list_filter = ['project']
    fieldsets = [
        (None, {'fields': ('project', 'title', 'url', 'description')}),
    ]


@admin.register(MLBackendTrainJob)
class MLBackendTrainJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'ml_backend', 'model_version', 'created_at', 'updated_at']
    list_filter = ['ml_backend']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
