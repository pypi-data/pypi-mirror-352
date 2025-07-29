from django.contrib import admin
from django.forms import ModelForm, PasswordInput
from users.models import User
from organizations.models import OrganizationMember
from django.contrib.auth.hashers import identify_hasher


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = []
        widgets = {
            'password': PasswordInput(attrs={'class': 'vTextField form-control'}, render_value=True)
        }


class UserOrganizationInline(admin.TabularInline):
    model = OrganizationMember
    fields = ['organization']
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = ['email', 'username', 'active_organization', 'is_active', 'is_staff', 'is_superuser', 'is_qa', 'is_qc', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'organization__title', 'active_organization__title']
    ordering = ['date_joined']
    inlines = [UserOrganizationInline]
    fieldsets = [
        ('Personal Information', {'fields': ('first_name', 'last_name')}),
        ('Account', {'fields': ('email', 'username', 'password')}),
        ('Organization', {'fields': ['active_organization']}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_qa','is_qc',)}),
    ]

    def save_model(self, request, obj, form, change):
        try:
            identify_hasher(obj.password)
        except ValueError:
            obj.set_password(obj.password)

        super().save_model(request, obj, form, change)
