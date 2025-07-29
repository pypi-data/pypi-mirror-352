"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
"""bn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import time

from core import views
from core.apis import GoogleLoginApi, GoogleLoginRedirectApi
from core.utils.common import collect_versions
from core.utils.static_serve import serve
from core.views import account_redirect, login_callback, login_redirect
from django.apps import apps
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import path, re_path
from django.views.generic.base import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from requests_oauthlib.oauth2_session import OAuth2Session
from rest_framework.permissions import AllowAny

# from .models import RemoteUser


# back compatibility: use `OAUTH_TOKEN_URL` if `OAUTH_REFRESH_TOKEN_URL` not present
OAUTH_REFRESH_TOKEN_URL = getattr(settings, 'OAUTH_REFRESH_TOKEN_URL', settings.OAUTH_TOKEN_URL)


def oauth_session(
    token=None,
    client_id=settings.OAUTH_CLIENT_ID,
    redirect_uri=settings.OAUTH_CALLBACK_URL,
    auto_refresh_url=settings.OAUTH_SERVER + OAUTH_REFRESH_TOKEN_URL,
    scope=getattr(settings, 'OAUTH_SCOPE', None),
    **kwargs
):

    return OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        auto_refresh_url=auto_refresh_url,
        token=token,
        scope=scope,
        **kwargs
    )


def get_login_url():
    oauth = oauth_session()
    auth_url = settings.OAUTH_SERVER + settings.OAUTH_AUTHORIZATION_URL
    authorization_url, state = oauth.authorization_url(auth_url, approval_prompt="auto")
    return dict(
        authorization_url=authorization_url,
        state=state,
    )


def sync_user(user, userdata):
    """Overwrite user details with data from the remote auth server"""

    for k in ['email', 'first_name', 'last_name']:
        if getattr(user, k) != userdata[k]:
            setattr(user, k, userdata[k])

    user.save()

    try:
        from allauth.account.models import EmailAddress
    except ImportError:
        return

    # Sync email address list
    for e in user.emailaddress_set.all():
        if e.email not in userdata['email_addresses']:
            e.delete()

    for e in userdata['email_addresses']:
        if user.emailaddress_set.filter(email=e).exists():
            continue
        emailaddress = EmailAddress(email=e, user=user)
        emailaddress.save()


def create_user(userdata):
    """Create user with proper RemoteUser relationship

    :param userdata: user details
    :return: User, is_new
    """
    user_model = get_user_model()
    is_new = False

    try:
        user = user_model.objects.get(
            remoteuser__remote_username=userdata['username']
        )
    except user_model.DoesNotExist:
        # Create user
        max_len = user_model._meta.get_field("username").max_length

        new_username = userdata['username'][:max_len]
        i = 0
        while user_model.objects.filter(username=new_username).exists():
            if i > 1000:
                return None
            i += 1
            new_username = userdata['username'][:max_len - len(str(i))] + str(i)

        user = user_model.objects.create_user(
            username=new_username,
            email=userdata['email'],
            first_name=userdata['first_name'],
            last_name=userdata['last_name'],
        )
        user.save()

        # user.remoteuser = RemoteUser(
        #     user=user, remote_username=userdata['username']
        # )
        # user.remoteuser.save()

        is_new = True

    return user, is_new


handler500 = 'core.views.custom_500'

versions = collect_versions()
schema_view = get_schema_view(
    openapi.Info(
        title="AiXBlock API",
        default_version='v' + versions['release'],
        contact=openapi.Contact(url="https://aixblock.io"),
        x_logo={"url": "../../static/icons/logo.png"}
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    re_path(r'^$', views.main, name='main'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
    re_path(r'^frontend/(?P<path>.*)$', serve, kwargs={'document_root': settings.EDITOR_ROOT, 'show_indexes': True}),
    re_path(r'^ui/(?P<path>.*)$', serve, kwargs={'document_root': settings.UI_ROOT, 'show_indexes': True}),
    re_path(r'^ria/(?P<path>.*)$', serve, kwargs={'document_root': settings.RIA_ROOT, 'show_indexes': True}),
    re_path(r'^tde/(?P<path>.*)$', serve, kwargs={'document_root': settings.TDE_ROOT, 'show_indexes': True}),
    re_path(r'^llm/(?P<path>.*)$', serve, kwargs={'document_root': settings.LLM_ROOT, 'show_indexes': True}),
    re_path(r'^static/fonts/roboto/roboto.css$', views.static_file_with_host_resolver('static/fonts/roboto/roboto.css', content_type='text/css')),
    re_path(r'^static/(?P<path>.*)$', serve, kwargs={'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    re_path(r'^temp/(?P<path>.*)$', serve, kwargs={'document_root': settings.UPLOAD_TEMP_DIR, 'show_indexes': False, 'delete_key': settings.UPLOAD_TEMP_DELETE_KEY, 'delete_token': settings.UPLOAD_TEMP_DELETE_TOKEN}),
    re_path(r'^admin/', views.fallback, name="admin-frontend"),
    re_path(r'^computes-supplier/', views.fallback, name="computes-supplier-frontend"),
    re_path(r'^models-seller/', views.fallback, name="models-seller-frontend"),
    re_path(r'^wallet/', views.fallback, name="wallet-frontend"),
    re_path(r'^pricing/', views.fallback, name="pricing-frontend"),
    re_path(r'^models-marketplace/', views.fallback, name="models-marketplace-frontend"),
    re_path(r'^user/signup/', views.fallback, name="user-signup-frontend"),
    path('user/wallet/', views.fallback, name="user-wallet-frontend"),

    re_path(r'^', include('organizations.urls')),
    re_path(r'^', include('projects.urls')),
    re_path(r'^', include('data_import.urls')),
    re_path(r'^', include('data_manager.urls')),
    re_path(r'^', include('data_export.urls')),
    re_path(r'^', include('users.urls')),
    re_path(r'^', include('tasks.urls')),
    re_path(r'^', include('io_storages.urls')),
    re_path(r'^', include('ml.urls')),
    re_path(r'^', include('webhooks.urls')),
    re_path(r'^', include('labels_manager.urls')),
    re_path(r'^', include('comments.urls')),
    re_path(r'^', include('compute_marketplace.urls')),
    re_path(r'^', include('model_marketplace.urls')),
    re_path(r'^', include('annotation_template.urls')),
    re_path(r'^', include('computes.urls')),
    re_path(r'^', include('tutorials.urls')),
    re_path(r'^', include('orders.urls')),
    re_path(r'^', include('reward_point.urls')),
    re_path(r'^', include('paypal.urls')),
    re_path(r'^', include('configs.urls')),
    re_path(r'^', include('stripe_payment.urls')),
    re_path(r'^', include('workflows.urls')),

    re_path(r'data/local-files/', views.localfiles_data, name="localfiles_data"),

    re_path(r'version/', views.version_page, name="version"),  # html page
    re_path(r'api/version/', views.version_page, name="api-version"),  # json response

    re_path(r'health/', views.health, name="health"),
    re_path(r'metrics/', views.metrics, name="metrics"),
    re_path(r'trigger500/', views.TriggerAPIError.as_view(), name="metrics"),

    re_path(r'samples/time-series.csv', views.samples_time_series, name="static_time_series"),
    re_path(r'samples/paragraphs.json', views.samples_paragraphs, name="samples_paragraphs"),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.with_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),

    path('docs/api/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #path('docs/', RedirectView.as_view(url='/static/docs/public/guide/introduction.html', permanent=False), name='docs-redirect'),

    # path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('feature-flags/', views.feature_flags, name='feature_flags'),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #####https://django-oauth-toolkit.readthedocs.io/en/latest/install.html
    #####python manage.py migrate oauth2_provider
    #pip install django-oauth-toolkit
    #path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    re_path(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    #oauth client
    re_path(r'^oauth/login/callback', login_callback, name='oauth2_client_login_callback'),
    re_path(r'^login', login_redirect, name='oauth2_client_login_redirect'),
    re_path(r'^account', account_redirect, name='oauth2_client_account_redirect'),

    path("callback/", GoogleLoginApi.as_view(), name="callback-raw"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect-raw"),
    path("computes-marketplace/", views.fallback, name="computes-marketplace"),
    path("models-marketplace/", views.fallback, name="models-marketplace"),
    path("models-seller/", views.fallback, name="models-seller"),
    path("computes-supplier/", views.fallback, name="ccomputes-supplier"),
    path("admin/organization/", views.fallback, name="admin_organization"),
    path("admin/template/", views.fallback, name="cadmin_template"),
    path("admin/user/", views.fallback, name="admin_user"),
    path("admin/compute/catalog/", views.fallback, name="admin_compute_catalog"),
    path("admin/compute/computes/", views.fallback, name="admin_compute_computes"),
    path("admin/model/catalog/", views.fallback, name="admin_model_catalog"),
    path("admin/model/models/", views.fallback, name="admin_model_models"),
    path("admin/subscription/plan", views.fallback, name="admin_subscription_plan"),
    path("admin/subscription/subscription", views.fallback, name="admin_subscription_subscription"),
    path("document/", views.fallback, name="document"),
    path("predict/rectangle", views.predict_rectangle, name="predict_rectangle"),
    path("predict/polygon", views.predict_polygon, name="predict_polygon"),
    path("predict/sam", views.predict_sam, name="predict_sam"),
    path('dashboard/', views.fallback, name="dashboard"),
    re_path(r'train-and-deploy', views.fallback, name="train_and_deploy_flow"),
    re_path(r'fine-tune-and-deploy', views.fallback, name="fine_tune_and_deploy_flow"),
    re_path(r'deploy', views.fallback, name="deploy_flow"),
    re_path(r'label-and-validate-data', views.fallback, name="label_and_validate_data_flow"),
    re_path(r'rented-models', views.fallback, name="rented_models"),
    re_path(r'self-host', views.fallback, name="self_host"),
    re_path(r'lease-out-compute', views.fallback, name="lease_out_compute"),
    re_path(r'commercialize-my-models', views.fallback, name="commercialize_my_models"),
    re_path(r'infrastructure', views.fallback, name="infrastructure"),
    re_path(r'first-time', views.fallback, name="first-time"),
    re_path(r'workflows', views.fallback, name="workflows"),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass

