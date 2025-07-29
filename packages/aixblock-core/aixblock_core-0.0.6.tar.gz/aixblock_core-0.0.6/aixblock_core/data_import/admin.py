from django.contrib import admin
from data_import.models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'file', 'user']
    list_filter = ['project', 'user']
    fieldsets = [
        (None, {'fields': ('project', 'file', 'user')}),
    ]
