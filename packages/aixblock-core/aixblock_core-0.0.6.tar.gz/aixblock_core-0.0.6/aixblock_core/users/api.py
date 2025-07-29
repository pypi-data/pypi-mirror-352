"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import logging
import urllib.parse

import drf_yasg.openapi as openapi
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema, no_body
from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import MethodNotAllowed
from rest_framework import status
from django.conf import settings

from core.permissions import all_permissions, ViewClassPermission, IsSuperAdmin
from tasks.models import Task
from organizations.models import Organization 
import re

from users.models import UserRole, User, Notification
from users.serializers import UserSerializer, NotificationSerializer, UserAdminViewSerializer, AdminUserListSerializer, \
    ValidateEmailSerializer, DetailNotificationSerializer
from users.serializers import UserCompactSerializer, UserRegisterSerializer, ChangePasswordSerializer, ResetPasswordSerializer
from users.functions import check_avatar, send_email_verification, is_valid_email, generate_username
from users.reward_point_register import reward_point_register
from organizations.models import OrganizationMember
from core.utils.paginate import SetPagination
from django.contrib.auth.hashers import make_password
from core.utils.common import create_hash
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.urls import reverse
from datetime import datetime, timedelta
from django.shortcuts import render
from compute_marketplace.models import Portfolio
from django.forms.models import model_to_dict
from .serializers import PortfolioSerializer
from plugins.plugin_centrifuge import generate_centrifuge_jwt
from users.serializers import TransactionSerializer
from users.models import Transaction

from core.settings.base import MAIL_SERVER
DOCKER_API = "tcp://69.197.168.145:4243"
from users.service_notify import send_email_thread
import threading
import csv

logger = logging.getLogger(__name__)


@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Save user details',
    operation_description="""
    Save details for a specific user, such as their name or contact information, in AiXBlock.
    """,
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='User ID'),
    ],
    request_body=UserSerializer
))
@method_decorator(name='list', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='List users',
        operation_description='List the users that exist on the AiXBlock server.'
    ))
@method_decorator(name='create', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Create new user',
        operation_description='Create a user in AiXBlock.',
        request_body=UserSerializer
    ))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Get user info',
        operation_description='Get info about a specific AiXBlock user, based on the user ID.',
        manual_parameters = [
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='User ID'),
                ],
    ))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Update user details',
        operation_description="""
        Update details for a specific user, such as their name or contact information, in AiXBlock.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='User ID'),
        ],
        request_body=UserSerializer
    ))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Delete user',
        operation_description='Delete a specific AiXBlock user.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='User ID'),
        ],
    ))
class UserAPI(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects

    @swagger_auto_schema(methods=['delete', 'post'])
    @action(detail=True, methods=['delete', 'post'])
    def avatar(self, request, pk):
        try:
            if request.method == 'POST':
                avatar = check_avatar(request.FILES)
                request.user.avatar = avatar
                request.user.save()
                return Response({'detail': 'avatar saved'}, status=200)

            elif request.method == 'DELETE':
                request.user.avatar = None
                request.user.save()
                return Response(status=200)
        except ValidationError as e:
            return Response(e, status=400)
        except Exception as e:
            return Response(e, status=500)

    @swagger_auto_schema(
        methods=['post'],
        request_body=no_body,
        responses={
            200: "Success",
        }
    )
    @action(detail=False, methods=['post'])
    def send_verification_email(self, request):
        user = request.user
        domain_verify = settings.BASE_BACKEND_URL
        if "Origin" in self.request.headers and self.request.headers["Origin"] != domain_verify:
            domain_verify = self.request.headers["Origin"]

        send_email_verification(user, domain_verify)
        return Response(status=200)

    def update(self, request, *args, **kwargs):
        # if request.data["is_qa"]:
        user_id = self.kwargs["pk"]
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            try:
                from organizations.models import Organization_Project_Permission
                is_qa = request.data["is_qa"]
                is_qc = request.data["is_qc"]
                user_role = Organization_Project_Permission.objects.filter(user_id=user_id, project_id=project_id, deleted_at__isnull=True).order_by("-id").first()
                if not user_role:
                    user_role = Organization_Project_Permission.objects.create(user_id=user_id, project_id=project_id, is_qa=user_role.is_qa, is_qc=user_role.is_qc)
                else:
                    user_role.is_qa = is_qa
                    user_role.is_qc = is_qc
                    user_role.save()

                response = {
                    "is_qa": user_role.is_qa,
                    "is_qc": user_role.is_qc
                }

                return Response(response, status=200)
            except Exception as e:
                pass

        old_serializer = self.serializer_class
        
        if not request.user.is_superuser and str(request.user.id) != user_id:
            return Response({"detail": f"You can only update your information or only super users can update other users' information."}, status=400)

        self.serializer_class = AdminUserListSerializer
        password_payload = request.data.get('password', '')

        if not request.user.is_superuser:
            ALLOWED_FIELDS = ['first_name', 'last_name', 'username', 'avatar', 'phone', 'initials']

            filtered_data = {
                key: value for key, value in request.data.items() 
                if key in ALLOWED_FIELDS
            }

            request._full_data = filtered_data

        if password_payload and len(password_payload) > 0 and str(request.user.id) == user_id:
            request.data['password'] = make_password(password_payload)

        response = super(UserAPI, self).update(request, *args, **kwargs)
        self.serializer_class = old_serializer
        return response

    def list(self, request, *args, **kwargs):
        return super(UserAPI, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if 'password' in request.data and len(request.data['password']) > 0:
            request.data['password'] = make_password(request.data['password'])
        if 'active_organization' not in request.data:
            request.data['active_organization'] = self.request.user.active_organization_id
        if User.objects.filter(username=request.data['username']).exists():
            error_response = {
                'status_code': status.HTTP_400_BAD_REQUEST,
                'validation_errors': {'username': ['User with this username already exists.']},
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        return super(UserAPI, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        User.objects.filter(email=serializer.initial_data['email']).update(password=serializer.initial_data['password'])
        self.request.user.active_organization.add_user(instance)

    def retrieve(self, request, *args, **kwargs):
        return super(UserAPI, self).retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        result = super(UserAPI, self).partial_update(request, *args, **kwargs)

        # newsletters
        if 'allow_newsletters' in request.data:
            user = User.objects.get(id=request.user.id)  # we need an updated user
            request.user.advanced_json = {  # request.user instance will be unchanged in request all the time
                'email': user.email, 'allow_newsletters': user.allow_newsletters,
                'update-notifications': 1, 'new-user': 0
            }
        return result

    def destroy(self, request, *args, **kwargs):
        return super(UserAPI, self).destroy(request, *args, **kwargs)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='List users for Admin',
    operation_description='List the users that exist on the AiXBlock server from admin view.',
    manual_parameters=[
        Parameter(name="search", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
    ]))
class UserListAdminViewAPI(generics.ListAPIView):
    parser_classes = (JSONParser,)
    permission_classes = (AllowAny, )
    pagination_class = SetPagination
    serializer_class = UserSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        queryset = User.objects.order_by('-id')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        return queryset

    def get(self, *args, **kwargs):
        return super(UserListAdminViewAPI, self).get(*args, **kwargs)

@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Reset user token',
        operation_description='Reset the user token for the current user.',
        responses={
            201: openapi.Response(
                description='User token response',
                schema=openapi.Schema(
                    description='User token',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(
                            description='Token',
                            type=openapi.TYPE_STRING
                        )
                    }
                ))
        }))
class UserResetTokenAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        token = user.reset_token()
        logger.debug(f'New token for user {user.pk} is {token.key}')
        return Response({'token': token.key}, status=201)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Get user token',
        operation_description='Get a user token to authenticate to the API as the current user.',
        responses={
            200: openapi.Response(
                description='User token response',
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        description='Token',
                        type=openapi.TYPE_STRING
                    )
                }
            )
        }))
class UserGetTokenAPI(APIView):
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        token = Token.objects.filter(user=user.id).first()
        if not token:
            return Response({'token': ''}, status=200)
        return Response({'token': token.key}, status=200)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Retrieve my user',
        operation_description='Retrieve details of the account that you are using to access the API.'
    ))
class UserWhoAmIAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        import os
        if os.getenv('RUNNING_CRONJOB') != '1':
            from compute_marketplace.schedule_func import start_thread_cron
            
        user = self.request.user
        centrifuge_token = generate_centrifuge_jwt(user.id)
        setattr(user, "centrifuge_token", centrifuge_token)

        if not user.username or len(user.username) == 0:
            user.username = generate_username()
            user.save()

        try:
            if user.id not in user.active_organization.active_members.values_list("user_id", flat=True):
                user.active_organization = None
            # user is organization member
            if user.active_organization is None:
                org_pk = Organization.find_by_user(user).pk
                user.active_organization_id = org_pk
                user.save(update_fields=['active_organization'])
        except Exception as e:
            print(e)
            
        return user

    def get(self, request, *args, **kwargs):
        return super(UserWhoAmIAPI, self).get(request, *args, **kwargs)


class UserSwitchOrganizationAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        organization_id = request.data.get("organization_id", None)
        organization_member = OrganizationMember.objects.filter(organization=organization_id, user=user).first()

        if organization_member is None:
            return Response({"message": "No member found for organization #" + organization_id.__str__()}, status=400)
        else:
            user.active_organization = organization_member.organization
            user.save()

        return Response({}, status=200)


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Get notifications',
        operation_description='Get notification of current user.'
    ))
class NotificationAPI(generics.ListAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).all()

    def get(self, request, *args, **kwargs):
        return super(NotificationAPI, self).get(request, *args, **kwargs)


class NotificationActionAPI(APIView):
    parser_classes = (JSONParser,)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        action = request.data.get("action", None)

        if action == "mark_all_read":
            Task.objects.filter(user=user).filter(is_read=False).update(is_read=True)
            return Response({}, status=200)
        elif action == "mark_read":
            notification_id = int(request.data.get("id", None))
            notification = Notification.objects.filter(user=user).filter(id=notification_id)

            if notification:
                notification.update(is_read=True)
                return Response({}, status=200)
            else:
                return Response({}, status=400)

        return Response({}, status=400)

@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Get notifications',
        operation_description='Get notification of current user.'
    ))
class DetailNotificationComputeAPI(generics.ListAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = DetailNotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        history_id = self.kwargs.get('history_id')
        return Notification.objects.filter(history_id=history_id).all()

    def get(self, request, *args, **kwargs):
        return super(DetailNotificationComputeAPI, self).get(request, *args, **kwargs)

# @method_decorator(name='get', decorator=swagger_auto_schema(
#         tags=['Users'],
#         operation_summary='Get deltail compute notifications',
#         operation_description='Get notification deltail of compute.'
#     ))
# class DetailNotificationComputeAPI(generics.ListAPIView):
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     permission_classes = (IsAuthenticated, )
#     serializer_class = DetailNotificationSerializer
#     pagination_class = NotificationPagination

#     def get_queryset(self):
#         history_id = self.kwargs.get('history_id')
#         return Notification.objects.filter(history_id=history_id).all()

#     def get(self, request, *args, **kwargs):
#         return super(DetailNotificationComputeAPI, self).get(request, *args, **kwargs)
    
@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Get simple user information',
    operation_description='Get simple information about a user.',
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='User ID'),
    ],
    ))
class UserGetSimpleAPI(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserCompactSerializer

    def retrieve(self, request, *args, **kwargs):
        return super(UserGetSimpleAPI, self).retrieve(request, *args, **kwargs)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='SignUp An User',
))

class UserRegisterApi(generics.CreateAPIView):
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = self.request.data.get('email')
        email = email.strip().lower()
        check = User.objects.filter(email=email)
        
        # import dns.resolver
        # _, domain = email.split("@")
        # try:
        #     records = dns.resolver.query(domain, 'MX')
        #     mxRecord = records[0].exchange
        #     mxRecord = str(mxRecord)
        # except:
        #     return Response({'error': 'Your domain email is wrong'}, status=400)

        # return Response({'error': 'Your email is taken'}, status=400)
        if check:
            return Response({'error': 'Your email is taken'}, status=400)

        email_validate = is_valid_email(email)
        email_verified = False

        # In case the validate API not working, user still can signup and verify their account.
        if not email_validate['has_error']:
            if email_validate['is_valid']:
                # If the email address is valid, they won't be asked for the email verify
                email_verified = True
            else:
                return Response({'error': 'Your email address is not valid'}, status=400)

        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        role = serializer.validated_data.pop('role')
        user = User.objects.create(
            **serializer.validated_data,
            username=serializer.validated_data["email"],
            is_verified=email_verified,
        )
        if role == UserRole.compute_supplier:
            user.is_compute_supplier = True
        elif role == UserRole.model_seller:
            user.is_model_seller = True
        elif role == UserRole.labeler:
            user.is_labeler = True

        token = create_hash()
        team_id = create_hash()
        status = "actived"

        organization = Organization.objects.create(
            title=email,
            created_by=user,
            token=token,
            team_id=team_id,
            status=status
        )

        OrganizationMember.objects.create(organization=organization, user=user, is_admin=True,)

        html_file_path =  './aixblock_labeltool/templates/mail/register.html'
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # notify_reponse = ServiceSendEmail(DOCKER_API)
        send_to = user.username if user.username else user.email
        html_content = html_content.replace('[user]', f'{send_to}')

        data = {
            "subject": "Welcome to AIxBlock - Registration Successful!",
            "from": "noreply@aixblock.io",
            "to": [f"{user.email}"],
            "html": html_content,
            # "text": "Welcome to AIxBlock!",
        }

        docket_api = "tcp://69.197.168.145:4243"
        host_name = MAIL_SERVER
        _send_mail = True
        if "Host" in self.request.headers:
            if "app.aixblock.io" not in self.request.headers["Host"] and "stag.aixblock.io" not in self.request.headers["Host"]:
                _send_mail = False
                
        if _send_mail:
            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
            email_thread.start()

        # if response != 202:
        #     user.delete()
        #     organization.delete()
        #     return Response({'error': 'Your email is taken'}, status=400)

        user.active_organization = organization
        user.save()

        if settings.REGISTER_TOPUP > 0:
            reward_point_register(user, topup_amount=settings.REGISTER_TOPUP)

        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return Response({'message': 'Register successful'}, status=201)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='User Info',
))
class UserInfoAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        centrifuge_token = generate_centrifuge_jwt(user.id)
        return Response(
            {
                "message": "User info",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "centrifuge_token": centrifuge_token,
                },
            },
            status=200,
        )

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='User Info From Oauths',
))
class Oauth2UserInfoAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission

    def post(self, request, *args, **kwargs):
        from oauth2_provider.models import AccessToken

        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Token '):
            return Response({"detail": "Authorization header failed."}, status=status.HTTP_400_BAD_REQUEST)

        token_value = auth_header.split(' ')[1]

        try:
            access_token = AccessToken.objects.get(token=token_value)
            user = access_token.user

            return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser,
            },
            status=200,
        )
        
        except AccessToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)
        
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Change Password',
    request_body=ChangePasswordSerializer,
))

class UserChangePassword(generics.ListAPIView):
    serializer = ChangePasswordSerializer
    def post(self, request, *args, **kwargs):
        email = self.request.data.get("email").lower()
        user = User.objects.filter(email = email).first()
        old_password = self.request.data.get("old_password")
        new_password = self.request.data.get("new_password")

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response({"Wrong password."}, status=status.HTTP_400_BAD_REQUEST)

        if old_password == new_password:
            return Response({"New password must be different from old password."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Reset Password',
    request_body=ResetPasswordSerializer,
))
class PasswordResetView(generics.ListAPIView):
    serializer = ResetPasswordSerializer
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission
    def post(self, request):
        domain_reset = settings.BASE_BACKEND_URL
        if "Origin" in self.request.headers and self.request.headers["Origin"] != domain_reset:
            domain_reset = self.request.headers["Origin"]
        email = self.request.data.get("email").lower()
        user = User.objects.filter(email=email).first()
        if user:
            token_generator = PasswordResetTokenGenerator()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator._make_token_with_timestamp(user, int((datetime.now() + timedelta(minutes=60*24)).timestamp()))
            reset_link = f'{domain_reset}/user/reset-password/?uidb64={uidb64}&token={token}'
            reset_link = re.sub(r'(?<!:)//+', '/', reset_link)
            send_to = user.username if user.username else user.email
            html_file_path =  './aixblock_labeltool/templates/mail/reset-password.html'

            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            # notify_reponse = ServiceSendEmail(DOCKER_API)
            html_content = html_content.replace('[user]', f'{send_to}')
            html_content = html_content.replace('[Link_reset]', reset_link)

            # html =  f"""<!DOCTYPE html><html lang="en"><body><p>Hi {send_to},</p><p>You recently requested to reset your password for your AIxBlock account.</p><p>Please click the link below to set up a new password</p><p><a href="{reset_link}">{reset_link}</a></p><p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p><p>Best Regards,</p><p>The AIxBlock Team</p><p><em>Note: This link will expire in 24 hours.</em></p></body></html>"""
            data = {
                "subject": "Reset Your Password AIxBlock",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": 'Reset password',
            }
            # notify_reponse.send_email(data)
            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
            email_thread.start()
            
            return Response({'detail': 'Password reset email has been sent.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No user found with this email address.'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Password reset request done',
))
class PasswordResetDoneView(APIView):
    def get(self, request):
        return Response({'detail': 'Password reset request done.'}, status=status.HTTP_200_OK)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Confirm password reset',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['new_password'],
        properties={
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
        },
    ),
    manual_parameters=[
        openapi.Parameter(
            name='uidb64',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='User ID encoded in base64',
        ),
        openapi.Parameter(
            name='token',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Token for password reset',
        ),
    ],
    responses={
        200: openapi.Response(description='Password has been reset successfully.'),
        400: openapi.Response(description='Invalid user or token.'),
    }
))
class PasswordResetConfirmView(generics.ListAPIView):
    serializer = ResetPasswordSerializer
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission

    def get(self, request, uidb64, token):
        try:
            uidb64 = self.kwargs.get('uidb64')
            token = self.kwargs.get('token')
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if PasswordResetTokenGenerator().check_token(user, token):
                # return render(request, 'users/user_login.html')
                return Response({'detail': 'Successfull'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, **kwargs):
        try:
            uidb64 = self.kwargs.get('uidb64')
            token = self.kwargs.get('token')
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if PasswordResetTokenGenerator().check_token(user, token):
                new_password = self.request.data.get('new_password')
                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Password reset complete',
))
class PasswordResetCompleteView(APIView):
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission
    def get(self, request):
        return Response({'detail': 'Password reset complete.'}, status=status.HTTP_200_OK)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["Users"],
        operation_summary="Get Portfolio",
        manual_parameters=[
            openapi.Parameter(
                "token_symbol",
                openapi.IN_QUERY,
                description="Token Symbol",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={200: PortfolioSerializer(many=False)},
    ),
)
class GetPortfolio(generics.RetrieveAPIView):
    def get_object(self):
        user_id = self.request.user.id
        token_symbol = self.request.query_params.get("token_symbol")

        if user_id and token_symbol:
            queryset = Portfolio.objects.filter(
                account_id=user_id, token_symbol=token_symbol
            )
            if queryset.exists():
                return queryset.first()
        return None

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": "Portfolio not found."}, status=status.HTTP_404_NOT_FOUND
            )
        instance_dict = model_to_dict(instance)
        return Response(instance_dict, status=status.HTTP_200_OK)


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["Users"],
        operation_summary="Deposit Portfolio",
        manual_parameters=[
            openapi.Parameter(
                "token_symbol",
                openapi.IN_QUERY,
                description="Token Symbol",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "amount_deposit",
                openapi.IN_QUERY,
                description="deposit amount",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={200: PortfolioSerializer(many=False)},
    ),
)
class DepositPortfolio(generics.UpdateAPIView):
    def get_object(self):
        user_id = self.request.user.id
        token_symbol = self.request.query_params.get("token_symbol")

        if user_id and token_symbol:
            queryset = Portfolio.objects.filter(
                account_id=user_id, token_symbol=token_symbol
            )
            if queryset.exists():
                return queryset.first()
        return None

    def patch(self, request, *args, **kwargs):
        return Response(
            {"detail": "This API is deprecated"}, status=status.HTTP_200_OK
        )


class EmailVerifyView(generics.GenericAPIView):

    def get(self, request, pk, token, *args, **kwargs):
        user = User.objects.filter(id=pk).first()

        if not user:
            return HttpResponseNotFound()

        if PasswordResetTokenGenerator().check_token(user, token):
            user.is_verified = True
            user.save()
            return HttpResponseRedirect(redirect_to="/")

        return HttpResponseNotFound()


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Validate email address',
    request_body=ValidateEmailSerializer,
))
class ValidateEmailAPI(generics.ListAPIView):
    serializer = ValidateEmailSerializer
    authentication_classes = []  # disables authentication
    permission_classes = []  # disables permission

    def post(self, request):
        serializer = ValidateEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(is_valid_email(serializer.validated_data["email"]), status=status.HTTP_200_OK)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Update Token Jupyter Admin',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='token'),
        },
    ),
))
class UpdateTokenJupyterAdmin(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        from .functions import update_token_admin
        token_value = request.data.get('token')
        update_token_admin(token_value)
        
        return Response({"detail": "Done"}, status=200)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Download all users',
))
class AdminDownloadUsers(generics.RetrieveAPIView):
    queryset = User.objects.all().order_by("pk")
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="platform-users.csv"'},
        )
        writer = csv.writer(response, delimiter=",", dialect="excel")
        writer.writerow([
            "ID",
            "Email",
            "Username",
            "First name",
            "Last name",
            "Active?",
            "Verified?",
            "Superadmin?",
            "QA?",
            "QC?",
            "AI Builder?",
            "Compute Supplier?",
            "Model Seller?",
            "Labeler?",
            "Date joined",
        ])

        for user in self.get_queryset():
            writer.writerow([
                user.id,
                user.email,
                user.username,
                user.first_name,
                user.last_name,
                user.is_active,
                user.is_verified,
                user.is_superuser,
                user.is_qa,
                user.is_qc,
                not user.is_compute_supplier and not user.is_model_seller and not user.is_labeler and not user.is_freelancer,
                user.is_compute_supplier,
                user.is_model_seller,
                user.is_labeler or user.is_freelancer,
                user.date_joined,
            ])

        return response

class TransactionPagination(PageNumberPagination):
    page_size = 10  # Số mục mặc định mỗi trang
    page_size_query_param = 'page_size'  # Cho phép client tùy chỉnh số mục trên mỗi trang
    max_page_size = 100  # Số mục tối đa mỗi trang

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['User'],
    operation_summary='Get transaction',
    manual_parameters=[
        openapi.Parameter(
            'page', openapi.IN_QUERY, description="Page number",
            type=openapi.TYPE_INTEGER, default=1
        ),
        openapi.Parameter(
            'page_size', openapi.IN_QUERY, description="page size",
            type=openapi.TYPE_INTEGER, default=10
        ),
    ]
))

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['User'],
    operation_summary='Create transaction',
    request_body=TransactionSerializer
))

class TransactionAPI(generics.GenericAPIView):
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination
    queryset = Transaction.objects.all()

    def get_queryset(self):
        user_id = self.request.user.id
        return Transaction.objects.filter(user_id=user_id, status=Transaction.Status.SUCCESS).order_by("-id")

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            # Lấy các trường cần thiết từ request, sử dụng request.data.get()
            order_id = request.data.get('order_id', None)
            amount = request.data.get('amount', None)
            description = request.data.get('description', None)
            wallet_address = request.data.get('wallet_address', None)
            unit = request.data.get('unit', None)
            network = request.data.get('network', None)
            type_value = request.data.get('type', None)
            # Lưu ý: Bạn có thể bỏ qua user_id nếu muốn gán tự động từ request.user.id,
            # ngay cả khi trong request body có truyền user_id, bạn sẽ ghi đè lại.
            
            # Tạo đối tượng Transaction mới
            transaction = Transaction.objects.create(
                user_id=request.user.id,  # Gán user_id từ thông tin user đăng nhập
                order_id=order_id,
                amount=amount,
                description=description,
                wallet_address=wallet_address,
                unit=unit,
                network=network,
                type=type_value
            )
            
            # Sử dụng serializer để trả về dữ liệu mới tạo
            serializer = self.get_serializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['User'],
    operation_summary='Update transaction',
    request_body=TransactionSerializer,
    # manual_parameters=[
    #     openapi.Parameter(
    #         'pk', openapi.IN_PATH,
    #         description="ID transaction",
    #         type=openapi.TYPE_INTEGER
    #     )
    # ]
))
class UpdateTransactionAPI(generics.UpdateAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def patch(self, request, *args, **kwargs):
        try:
            transaction_id = request.data.get('id') or kwargs.get('pk')
            if not transaction_id:
                return Response(
                    {"error": "Transaction ID is required for update."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            transaction = Transaction.objects.get(id=transaction_id, user_id=request.user.id)
            serializer = self.get_serializer(transaction, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['User'],
    operation_summary='Delete transaction',
    # manual_parameters=[
    #     openapi.Parameter(
    #         'pk', openapi.IN_PATH,
    #         description="ID transaction",
    #         type=openapi.TYPE_INTEGER
    #     )
    # ]
))
class DeleteTransactionAPI(generics.DestroyAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            transaction_id = kwargs.get('pk')
            if not transaction_id:
                return Response(
                    {"error": "Transaction ID is required for delete."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            transaction = Transaction.objects.get(id=transaction_id, user_id=request.user.id)
            transaction.delete()
            return Response(
                {"message": "Transaction deleted successfully."},
                status=status.HTTP_200_OK
            )
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)