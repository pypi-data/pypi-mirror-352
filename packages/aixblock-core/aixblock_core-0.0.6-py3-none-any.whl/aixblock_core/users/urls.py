"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from os.path import join
from django.conf import settings
from django.conf.urls import url, include
from django.urls import path, re_path
from django.views.static import serve
from rest_framework import routers

import core.views
from users import views, api
from core import views as core_views
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

router = routers.DefaultRouter()
router.register(r'users', api.UserAPI, basename='user')

urlpatterns = [
    url(r"^api/", include(router.urls)),
    path("api/admin/users", api.UserListAdminViewAPI.as_view(), name="admin-list-user"),
    # Authentication
    path("user/login/", views.user_login, name="user-login"),
    path("user/signup/", views.user_signup, name="user-signup"),  # backend
    path(
        "user/reset-password/", views.user_reset_password, name="user-reset-password"
    ),  # reset password
    path("user/account/", views.user_account, name="user-account"),
    path("user/bulk/", views.user_bulk, name="user-bulk"),
    url(r"^logout/?$", views.logout, name="logout"),
    # avatars
    re_path(
        r"^data/" + settings.AVATAR_PATH + "/(?P<path>.*)$",
        serve,
        kwargs={"document_root": join(settings.MEDIA_ROOT, settings.AVATAR_PATH)},
    ),
    # Token
    path(
        "api/current-user/reset-token/",
        api.UserResetTokenAPI.as_view(),
        name="current-user-reset-token",
    ),
    path(
        "api/current-user/token",
        api.UserGetTokenAPI.as_view(),
        name="current-user-token",
    ),
    path(
        "api/current-user/whoami",
        api.UserWhoAmIAPI.as_view(),
        name="current-user-whoami",
    ),
    path(
        "api/current-user/switch-organization",
        api.UserSwitchOrganizationAPI.as_view(),
        name="current-user-switch-organization",
    ),
    path(
        "api/current-user/notifications",
        api.NotificationAPI.as_view(),
        name="current-user-notifications",
    ),
    path(
        "api/current-user/notification-action",
        api.NotificationActionAPI.as_view(),
        name="current-user-notification-action",
    ),
    path(
        "api/user/signup",
        api.UserRegisterApi.as_view(),
        name="current-user-notification-action",
    ),
    # User's simple information
    path(
        "api/user/<int:pk>/",
        api.UserGetSimpleAPI.as_view(),
        name="user-simple-information",
    ),
    path("user/organization", core_views.fallback, name="user-organization"),
    path("user", core_views.fallback, name="user-management"),
    path("notebook/", views.notebook, name="notebook"),
    path("api/user/info", api.UserInfoAPI.as_view(), name="user-info"),
    path("api/user/info/oauth2", api.Oauth2UserInfoAPI.as_view(), name="user-info-oauth2"),
    path("api/user/update-admin-token-jupyter", api.UpdateTokenJupyterAdmin.as_view(), name="update-admin-token-jupyter"),
    path("user/rewards", core_views.fallback, name="user-rewards"),
    path(
        "api/user/change-password",
        api.UserChangePassword.as_view(),
        name="change-password",
    ),
    path(
        "api/user/password-reset/",
        api.PasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "api/user/password-reset/done/",
        api.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "api/user/password-reset-confirm/<uidb64>/<token>/",
        api.PasswordResetConfirmView.as_view(),
        name="confirm-password-reset",
    ),
    path(
        "api/user/email-verify/<pk>/<token>/",
        api.EmailVerifyView.as_view(),
        name="email-verify",
    ),
    path(
        "api/user/password-reset-complete/",
        api.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("api/user/portfolio", api.GetPortfolio.as_view(), name="get_portfolio"),
    path("api/user/portfolio/deposit", api.DepositPortfolio.as_view(), name="deposit-amount"),
    path(
        "api/validate-email/",
        api.ValidateEmailAPI.as_view(),
        name="validate-email",
    ),
    # path("api/user/notification/<int:pk>", api.DetailNotificationAPI.as_view(), name="get_detail_noti"),
    path("api/user/notification/<history_id>", api.DetailNotificationComputeAPI.as_view(), name="detail compute notify"),
    path("api/user/export-all", api.AdminDownloadUsers.as_view(), name="export-users-list"),
]
