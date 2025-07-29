"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import io
import json
import logging
import mimetypes
import os
import posixpath
import sys
import urllib.parse
from pathlib import Path
from wsgiref.util import FileWrapper

import pandas as pd
import requests
from authlib.integrations.base_client import OAuthError
from authlib.integrations.django_client import OAuth
from django.contrib.auth.decorators import login_required

from core import utils
from core.feature_flags import all_flags
from core.label_config import generate_time_series_json
from core.google_login import GoogleRawLoginFlowService
from core.utils.common import collect_versions
from core.utils.io import find_file
from django import forms
from django.conf import settings
# from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.db.models import CharField, F, Value
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound, HttpResponseServerError,
                         JsonResponse, HttpResponseGone)
from django.shortcuts import redirect, reverse, render
from django.template import loader
from django.utils._os import safe_join
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from io_storages.localfiles.models import LocalFilesImportStorage
from ranged_fileresponse import RangedFileResponse
from rest_framework.views import APIView
from users.models import User

# from core.urls import get_login_url
# from core.utils import get_login_url


def login_redirect(request):
    request.session['next'] = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    urldata = {'authorization_url':''} #get_login_url()
    print(" => state: " + urldata['state'])
    request.session['oauth_login_state'] = urldata['state']
    return redirect(urldata['authorization_url'])


def account_redirect(request):
    return redirect(settings.OAUTH_SERVER + '/accounts')


def login_callback(request):
    if request.session.get('user', None) is not None:
        return redirect("/dashboard")

    if 'code' not in request.GET:
        raise PermissionDenied

    if 'state' not in request.GET:
        raise PermissionDenied

    if request.session.get('oauth_login_state') != request.GET['state']:
        raise PermissionDenied

    user = authenticate(code=request.GET['code'])

    if user is not None and user.is_active:
        auth_login(request, user)
        request.session['oauth_token'] = getattr(user, 'oauth_token', None)
        request.session['oauth_user_data'] = dict(synced_at=time())
        return redirect(request.session.get('next', settings.LOGIN_REDIRECT_URL))

    raise PermissionDenied


logger = logging.getLogger(__name__)
_PARAGRAPH_SAMPLE = None
from django.contrib import auth


def main(request):
    user = request.user

    if settings.OAUTH_ENABLE:
        oauth = OAuth()

        def update_token(token, refresh_token, access_token):
            request.session['token'] = token
            return None
        sso_client = oauth.register(
            settings.OAUTH_CLIENT_NAME, overwrite=True, **settings.OAUTH_CLIENT, update_token=update_token
        )

        if user.is_authenticated:
            if user.active_organization is None and 'organization_pk' not in request.session:
                logout(request)
                request.session.clear()
                return sso_client.authorize_redirect(request, settings.OAUTH_CLIENT['redirect_uri']) #redirect(reverse('user-login'))

            # business mode access
            return redirect('/dashboard/')

        # not authenticated
        request.session.clear()
        return sso_client.authorize_redirect(request, settings.OAUTH_CLIENT['redirect_uri']) #redirect(reverse('user-login'))

    if user.is_authenticated:
        return redirect('/dashboard/')
    else:
        next_page = request.GET.get('next')

        if next_page:
            return redirect(reverse('user-login') + "?next=" + urllib.parse.quote(next_page))

        return redirect(reverse('user-login'))


def version_page(request):
    """ Get platform version
    """
    # update latest version from pypi response
    # from aixblock_core.core.utils.common import check_for_the_latest_version
    # check_for_the_latest_version(print_message=False)
    http_page = request.path == '/version/'
    result = collect_versions(force=http_page)

    # html / json response
    if request.path == '/version/':
        # other settings from backend
        if request.user.is_superuser:
            result['settings'] = {key: str(getattr(settings, key)) for key in dir(settings)
                                  if not key.startswith('_') and not hasattr(getattr(settings, key), '__call__')}

        result = json.dumps(result, indent=2)
        result = result.replace('},', '},\n').replace('\\n', ' ').replace('\\r', '')
        return HttpResponse('<pre>' + result + '</pre>')
    else:
        return JsonResponse(result)


def health(request):
    """ System health info """
    logger.debug('Got /health request.')
    return HttpResponse(json.dumps({
        "status": "UP"
    }))


def metrics(request):
    """ Empty page for metrics evaluation """
    return HttpResponse('')


class TriggerAPIError(APIView):
    """ 500 response for testing """
    authentication_classes = ()
    permission_classes = ()

    @swagger_auto_schema(auto_schema=None)
    def get(self, request):
        raise Exception('test')


def editor_files(request):
    """ Get last editor files
    """
    response = utils.common.find_editor_files()
    return HttpResponse(json.dumps(response), status=200)


def custom_500(request):
    """ Custom 500 page """
    t = loader.get_template('500.html')
    type_, value, tb = sys.exc_info()
    return HttpResponseServerError(t.render({'exception': value}))


def samples_time_series(request):
    """ Generate time series example for preview
    """
    time_column = request.GET.get('time', '')
    value_columns = request.GET.get('values', '').split(',')
    time_format = request.GET.get('tf')

    # separator processing
    separator = request.GET.get('sep', ',')
    separator = separator.replace('\\t', '\t')
    aliases = {'dot': '.', 'comma': ',', 'tab': '\t', 'space': ' '}
    if separator in aliases:
        separator = aliases[separator]

    # check headless or not
    header = True
    if all(n.isdigit() for n in [time_column] + value_columns):
        header = False

    # generate all columns for headless csv
    if not header:
        max_column_n = max([int(v) for v in value_columns] + [0])
        value_columns = range(1, max_column_n+1)

    ts = generate_time_series_json(time_column, value_columns, time_format)
    csv_data = pd.DataFrame.from_dict(ts).to_csv(index=False, header=header, sep=separator).encode('utf-8')

    # generate response data as file
    filename = 'time-series.csv'
    response = HttpResponse(csv_data, content_type='application/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['filename'] = filename
    return response


def samples_paragraphs(request):
    """ Generate paragraphs example for preview
    """
    global _PARAGRAPH_SAMPLE

    if _PARAGRAPH_SAMPLE is None:
        with open(find_file('paragraphs.json'), encoding='utf-8') as f:
            _PARAGRAPH_SAMPLE = json.load(f)
    name_key = request.GET.get('nameKey', 'author')
    text_key = request.GET.get('textKey', 'text')

    result = []
    for line in _PARAGRAPH_SAMPLE:
        result.append({name_key: line['author'], text_key: line['text']})

    return HttpResponse(json.dumps(result), content_type='application/json')


def localfiles_data(request):
    """Serving files for LocalFilesImportStorage"""
    user = request.user
    path = request.GET.get('d')
    if settings.LOCAL_FILES_SERVING_ENABLED is False:
        return HttpResponseForbidden("Serving local files can be dangerous, so it's disabled by default. "
                                     'You can enable it with LOCAL_FILES_SERVING_ENABLED environment variable.')

    local_serving_document_root = settings.LOCAL_FILES_DOCUMENT_ROOT
    if path and request.user.is_authenticated:
        path = posixpath.normpath(path).lstrip('/')
        full_path = Path(safe_join(local_serving_document_root, path))
        user_has_permissions = False

        # Try to find Local File Storage connection based prefix:
        # storage.path=/home/user, full_path=/home/user/a/b/c/1.jpg =>
        # full_path.startswith(path) => True
        localfiles_storage = LocalFilesImportStorage.objects \
            .annotate(_full_path=Value(os.path.dirname(full_path), output_field=CharField())) \
            .filter(_full_path__startswith=F('path'))
        if localfiles_storage.exists():
            user_has_permissions = any(storage.project.has_permission(user) for storage in localfiles_storage)

        if user_has_permissions and os.path.exists(full_path):
            content_type, encoding = mimetypes.guess_type(str(full_path))
            content_type = content_type or 'application/octet-stream'
            return RangedFileResponse(request, open(full_path, mode='rb'), content_type)
        else:
            return HttpResponseNotFound()

    return HttpResponseForbidden()


def static_file_with_host_resolver(path_on_disk, content_type):
    """ Load any file, replace {{HOSTNAME}} => settings.HOSTNAME, send it as http response
    """
    path_on_disk = os.path.join(os.path.dirname(__file__), path_on_disk)

    def serve_file(request):
        with open(path_on_disk, 'r') as f:
            body = f.read()
            body = body.replace('{{HOSTNAME}}', settings.HOSTNAME)

            out = io.StringIO()
            out.write(body)
            out.seek(0)

            wrapper = FileWrapper(out)
            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Length'] = len(body)
            return response

    return serve_file


def feature_flags(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseForbidden()
    return HttpResponse(json.dumps(all_flags(request.user), indent=4), status=200)


########################################################################################################################
# GG Oauth views
########################################################################################################################
class GoogleLoginRedirectApi(View):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginApi(View):
    class InputValidationForm(forms.Form):
        code = forms.CharField(required=False)
        error = forms.CharField(required=False)
        state = forms.CharField(required=False)

    def get(self, request, *args, **kwargs):

        input_form = self.InputValidationForm(data=request.GET)

        if not input_form.is_valid():
            return

        validated_data = input_form.cleaned_data

        code = validated_data["code"] if validated_data.get("code") != "" else None
        error = validated_data["error"] if validated_data.get("error") != "" else None
        state = validated_data["state"] if validated_data.get("state") != "" else None

        if error is not None:
            return JsonResponse({"error": error}, status=400)

        if code is None or state is None:
            return JsonResponse({"error": "Code and state are required."}, status=400)

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return JsonResponse({"error": "CSRF check failed."}, status=400)

        del request.session["google_oauth2_state"]

        if state != session_state:
            return JsonResponse({"error": "CSRF check failed."}, status=400)

        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]

        user = User.objects.filter(email=user_email).last()

        if user is None:
            return JsonResponse({"error": f"User with email {user_email} is not found."}, status=404)

        login(request, user)

        result = {
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
        }

        return JsonResponse(result, status=200)


@login_required
def fallback(request, **kwargs):
    return render(request, 'fallback.html')


def predict(url, current_request):
    try:
        res = requests.request(current_request.method, url, data=current_request.body,
                               headers=current_request.headers)
    except Exception as e:
        return HttpResponseGone(content=json.dumps({
            "detail": "An error ocurred. Please try again.",
            "error": e.__str__(),
        }))

    return HttpResponse(res.content, status=res.status_code)


def predict_rectangle(request, **kwargs):
    return predict(settings.TOOLBAR_PREDICT_RECTANGLE, request)


def predict_polygon(request, **kwargs):
    return predict(settings.TOOLBAR_PREDICT_POLYGON, request)


def predict_sam(request, **kwargs):
    return predict(settings.TOOLBAR_PREDICT_SAM, request)
