"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import random
import string
import sys

import ujson as json
import time
# from django.core.serializers.json import DjangoJSONEncoder
from uuid import uuid4

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponsePermanentRedirect
# from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.base import BaseHandler
from django.core.exceptions import MiddlewareNotUsed
from django.middleware.common import CommonMiddleware
from django.conf import settings
from django.utils.http import escape_leading_slashes
from rest_framework.permissions import SAFE_METHODS
from core.utils.contextlog import ContextLog
from authlib.integrations.base_client import OAuthError
from authlib.integrations.django_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
# from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
# from requests_oauthlib.oauth2_session import OAuth2Session
from users.models import User
from django.contrib import auth
from organizations.models import Organization


class OAuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.oauth = OAuth()

    def process_request(self, request):
        if not settings.OAUTH_ENABLE:
            return self.get_response(request)

        if settings.OAUTH_URL_WHITELISTS is not None:
            for w in settings.OAUTH_URL_WHITELISTS:
                if request.path.startswith(w):
                    return self.get_response(request)

        def update_token(token, refresh_token, access_token):
            request.session['token'] = token
            return None

        sso_client = self.oauth.register(
            settings.OAUTH_CLIENT_NAME, overwrite=True, **settings.OAUTH_CLIENT, update_token=update_token
        )

        if request.session.get('token', None) is None:
            if 'api' in request.path or 'heath' in request.path:
                self.clear_session(request)
            elif request.path.startswith('/oauth/login/callback'):
                self.clear_session(request)
                request.session['token'] = sso_client.authorize_access_token(request)

            # if request.session.get('user', None) is None:
            #     if self.get_current_user(sso_client, request) is not None:
            #         redirect_uri = request.session.pop('redirect_uri', None)
            #         if redirect_uri is not None:
            #             return redirect(redirect_uri)
            #         return redirect(views.index)
            
        if request.session.get('token', None) is not None:
            current_user = request.session.get('user', None)

            if current_user is None:
                current_user = self.get_current_user(sso_client, request)

            # print(current_user)

            if current_user is not None:
                return self.get_response(request)

        # remember redirect URI for redirecting to the original URL.
        request.session['redirect_uri'] = request.path
        if request.path.startswith('/data/upload') == False and not request.path.startswith("/api") and  "/admin" not in request.path and not request.path.startswith("/health"):
            return sso_client.authorize_redirect(request, settings.OAUTH_CLIENT['redirect_uri'])
        elif "/admin" in request.path:
            if request.session.get('token', None) is None:
                request.session['redirect_uri'] = "/admin/login/"
                return
            else:
                request.session['redirect_uri'] = "/admin/"
                return
        else:
            return
    
    # fetch current login user info
    # 1. check if it's in cache
    # 2. fetch from remote API when it's not in cache
    @staticmethod
    def get_current_user(sso_client, request):
        token = request.session.get('token', None)
        if token is None or 'access_token' not in token:
            return None

        if not OAuth2Token.from_dict(token).is_expired() and 'user' in request.session:
            user = request.session['user']
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return user

        try:
            res = sso_client.get(
                settings.OAUTH_CLIENT['api_base_url'] + settings.OAUTH_CLIENT['userinfo_endpoint'],
                token=OAuth2Token(token)
            )

            info = res.json()

            if res.ok:
                user = User.objects.filter(email=info.get('email').lower()).last()

                if user is None:
                    user = User.objects.create_user(
                        email=info.get('email').lower(),
                        password=''.join(random.choice(string.ascii_lowercase) for _ in range(12)),
                        is_staff=True,
                        is_superuser=False
                    )

                team_ids = info.get('team_id') if info.get('team_id') is not None else []
                user_org = None

                for team_id in team_ids:
                    team_id = str(team_id)
                    current_org = Organization.find_by_team_id(team_id)

                    if current_org is None:
                        current_org = Organization.create_team_organization(
                            team_id=team_id,
                            created_by=user,
                        )
                    else:
                        if current_org.members.filter(user=user).first() is None:
                            current_org.add_user(user)

                    if user_org is None:
                        user_org = current_org

                if user_org is None:
                    try:
                        user_org = Organization.find_by_user(user)
                    except ValueError:
                        user_org = Organization.create_organization(
                            created_by=user,
                            title='User #' + str(user.id),
                        )
                        pass

                user.active_organization_id = user_org.pk
                user.save(update_fields=['active_organization'])
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['user'] = res.json()
                return user
        except OAuthError as e:
            print(e)

        return None
    
    @staticmethod
    def clear_session(request):
        try:
            del request.session['user']
            del request.session['token']
        except KeyError:
            pass

    def __del__(self):
        print('destroyed')


class StaticCacheHeader:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        if request.path.endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".webm", ".svg")):
            # Cache for 6 months
            response['Cache-Control'] = 'public, max-age=%d' % getattr(settings, 'CACHE_CONTROL_MAX_AGE', 15552000)

        return response


def enforce_csrf_checks(func):
    """ Enable csrf for specified view func
    """
    # USE_ENFORCE_CSRF_CHECKS=False is for tests
    if settings.USE_ENFORCE_CSRF_CHECKS:
        def wrapper(request, *args, **kwargs):
            return func(request, *args, **kwargs)

        wrapper._dont_enforce_csrf_checks = False
        return wrapper
    else:
        return func


class DisableCSRF(MiddlewareMixin):
    # disable csrf for api requests
    @staticmethod
    def process_view(request, callback, *args, **kwargs):
        # if hasattr(callback, '_dont_enforce_csrf_checks'):
        #     setattr(request, '_dont_enforce_csrf_checks', callback._dont_enforce_csrf_checks)
        # elif request.GET.get('enforce_csrf_checks'):  # _dont_enforce_csrf_checks is for test
        #     setattr(request, '_dont_enforce_csrf_checks', False)
        # else:
        setattr(request, '_dont_enforce_csrf_checks', True)


class HttpSmartRedirectResponse(HttpResponsePermanentRedirect):
    pass


class CommonMiddlewareAppendSlashWithoutRedirect(CommonMiddleware):
    """ This class converts HttpSmartRedirectResponse to the common response
        of Django view, without redirect. This is necessary to match status_codes
        for urls like /url?q=1 and /url/?q=1. If you don't use it, you will have 302
        code always on pages without slash.
    """
    response_redirect_class = HttpSmartRedirectResponse

    def __init__(self, *args, **kwargs):
        # create django request resolver
        self.handler = BaseHandler()

        # prevent recursive includes
        old = settings.MIDDLEWARE
        name = self.__module__ + '.' + self.__class__.__name__
        settings.MIDDLEWARE = [i for i in settings.MIDDLEWARE if i != name]

        self.handler.load_middleware()

        settings.MIDDLEWARE = old
        super(CommonMiddlewareAppendSlashWithoutRedirect, self).__init__(*args, **kwargs)

    def get_full_path_with_slash(self, request):
        """ Return the full path of the request with a trailing slash appended
            without Exception in Debug mode
        """
        new_path = request.get_full_path(force_append_slash=True)
        # Prevent construction of scheme relative urls.
        new_path = escape_leading_slashes(new_path)
        return new_path

    def process_response(self, request, response):
        response = super(CommonMiddlewareAppendSlashWithoutRedirect, self).process_response(request, response)

        request.editor_keymap = settings.EDITOR_KEYMAP

        if isinstance(response, HttpSmartRedirectResponse):
            if not request.path.endswith('/'):
                # remove prefix SCRIPT_NAME
                path = request.path[len(settings.FORCE_SCRIPT_NAME):] if settings.FORCE_SCRIPT_NAME \
                    else request.path
                request.path = path + '/'
            # we don't need query string in path_info because it's in request.GET already
            request.path_info = request.path
            response = self.handler.get_response(request)

        return response


class SetSessionUIDMiddleware(CommonMiddleware):
    def process_request(self, request):
        if 'uid' not in request.session:
            request.session['uid'] = str(uuid4())


class ContextLogMiddleware(CommonMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.log = ContextLog()

    def __call__(self, request):
        body = None
        try:
            body = json.loads(request.body)
        except:
            try:
                body = request.body.decode('utf-8')
            except:
                pass
        response = self.get_response(request)
        self.log.send(request=request, response=response, body=body)
        return response


class DatabaseIsLockedRetryMiddleware(CommonMiddleware):
    """Workaround for sqlite performance issues
    we wait and retry request if database is locked"""
    def __init__(self, get_response):
        super().__init__(get_response)
        if settings.DJANGO_DB != settings.DJANGO_DB_SQLITE:
            raise MiddlewareNotUsed()
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        retries_number = 0
        sleep_time = 1
        backoff = 1.5
        while (
            response.status_code == 500
            and hasattr(response, 'content')
            and b'database-is-locked-error' in response.content
            and retries_number < 15
        ):
            time.sleep(sleep_time)
            response = self.get_response(request)
            retries_number += 1
            sleep_time *= backoff
        return response


class UpdateLastActivityMiddleware(CommonMiddleware):
    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        if hasattr(request, 'user') and request.method not in SAFE_METHODS:
            if request.user.is_authenticated:
                request.user.update_last_activity()
