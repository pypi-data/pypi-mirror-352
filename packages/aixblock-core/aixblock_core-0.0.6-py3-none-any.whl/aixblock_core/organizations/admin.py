from django.contrib import admin
from django.utils.html import format_html
from organizations.models import Organization, OrganizationMember


class OrganizationUsersInline(admin.TabularInline):
    model = OrganizationMember
    fields = ['user']
    extra = 0


@admin.register(Organization)
class UserAdmin(admin.ModelAdmin):
    
    list_display = ['title', 'export_report', 'created_by', 'created_at']
    search_fields = ['title']
    ordering = ['created_at']
    inlines = [OrganizationUsersInline]
    fieldsets = [
        (None, {'fields': ('title', 'created_by')}),
        (None, {'fields': ('token', 'team_id')}),
    ]

    @admin.display(description='')
    def export_report(self, obj):
        # return format_html(f'<a href="/api/organizations/{obj.id}/report">Export Report</a>')
        
        return format_html(f'<button class="button" onClick="window.open(\'/organization/report\', \'Export Report\', \'width=700,height=400,toolbar=no,scrollbars=yes,resizable=yes\'); return false;"><span class="icon-plus">Export Report</span></button>')
    
