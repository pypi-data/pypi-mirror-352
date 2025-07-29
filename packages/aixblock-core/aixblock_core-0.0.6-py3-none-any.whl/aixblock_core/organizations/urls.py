"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.urls import include, path

from organizations import api, views

app_name = 'organizations'

# TODO: there should be only one patterns list based on API (with api/ prefix removed)
# Page URLs
_urlpatterns = [
    # get organization page
    path('', views.organization_people_list, name='organization-index'),
]

# API URLs
_api_urlpattens = [
    # organization list viewset
    path('', api.OrganizationListAPI.as_view(), name='organization-list'),
    path('update/<int:pk>', api.OrganizationPatchAPI.as_view(), name='organization-update'),
    path('delete/<int:pk>', api.OrganizationDeleteAPI.as_view(), name='organization-delete'),
    path('admin/', api.OrganizationListAdminViewAPI.as_view(), name='admin-organization-list'),
    path('admin/create', api.OrganizationCreateAPI.as_view(), name='admin-create-organization'),
    # organization detail viewset
    path('<int:pk>', api.OrganizationAPI.as_view(), name='organization-detail'),
    # organization memberships list viewset
    path('memberships/<int:pk>', api.OrganizationMembershipAPI.as_view(), name='organization-memberships'),
    path('<int:pk>/memberships', api.OrganizationMemberListAPI.as_view(), name='organization-memberships-list'),
    # organization report
    path('<int:pk>/report', api.OrganizationReportAPI.as_view(), name='organization-report'),
    path('<int:pk>/report/<int:pro>/<str:rol>', api.OrganizationReportAPI.as_view(), name='organization-report_get'),
    path('<int:pk>/projects', api.OrganizationProjectAPI.as_view(), name='organization-projects'),
    path('<int:pk>/users', api.OrganizationUserAPI.as_view(), name='organization-users'),
    path('role-user', api.RoleUserInProjectAPI.as_view(), name='organization-users'),
]

# TODO: these urlpatterns should be moved in core/urls with include('organizations.urls')
urlpatterns = [
    path('organization/', views.simple_view, name='organization-simple'),
    path('organization/webhooks', views.simple_view, name='organization-simple-webhooks'),

    path('people/', include(_urlpatterns)),
    path('api/organizations/', include((_api_urlpattens, app_name), namespace='api')),

    # invite
    path('api/invite', api.OrganizationInviteAPI.as_view(), name='organization-invite'),
    
    path('api/invite/csv', api.OrganizationInviteAPIByCSV.as_view(), name='organization-invite-csv'),
    path('api/organizations/remove-member', api.OrganizationRemoveMemberAPI.as_view(), name='organization-remove-member'),
    path('api/organizations/add-member-by-email', api.OrganizationAddMemberByEmailAPI.as_view(), name='organization-add-member-by-email'),
    path('api/invite/reset-token', api.OrganizationResetTokenAPI.as_view(), name='organization-reset-token'),
    path('organization/report', views.organization_export_report, name='organization-export-report'),
]
