"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import random
import string
import threading
import uuid
import os
from datetime import datetime, timedelta

import requests
from django import forms
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import redirect
from django.contrib import auth
from django.urls import reverse
from django.core.files.images import get_image_dimensions

from organizations.models import Organization
from core.utils.contextlog import ContextLog
from core.utils.common import load_func
from users.service_notify import send_email_thread
import base64
import hmac
import json
import hashlib
import time
import jwt
from core.settings.base import MAIL_SERVER
from core.settings.base import CENTRIFUGE_SECRET, HOST_JUPYTERHUB, ADMIN_JUPYTERHUB_TOKEN


def hash_upload(instance, filename):
    filename = str(uuid.uuid4())[0:8] + '-' + filename
    return settings.AVATAR_PATH + '/' + filename


def check_avatar(files):
    images = list(files.items())
    if not images:
        return None

    filename, avatar = list(files.items())[0]  # get first file
    w, h = get_image_dimensions(avatar)
    if not w or not h:
        raise forms.ValidationError("Can't read image, try another one")

    # validate dimensions
    max_width = max_height = 1200
    if w > max_width or h > max_height:
        raise forms.ValidationError('Please use an image that is %s x %s pixels or smaller.'
                                    % (max_width, max_height))

    # validate content type
    main, sub = avatar.content_type.split('/')
    if not (main == 'image' and sub.lower() in ['jpeg', 'jpg', 'gif', 'png']):
        raise forms.ValidationError(u'Please use a JPEG, GIF or PNG image.')

    # validate file size
    max_size = 1024 * 1024
    if len(avatar) > max_size:
        raise forms.ValidationError('Avatar file size may not exceed ' + str(max_size/1024) + ' kb')

    return avatar


def save_user(request, next_page, user_form):
    """ Save user instance to DB
    """
    user = user_form.save()
    user.username = user.email.split('@')[0]
    user.save()

    if Organization.objects.exists():
        org = Organization.objects.first()
        org.add_user(user)
    else:
        org = Organization.create_organization(created_by=user, title='AiXBlock')
    user.active_organization = org
    user.save(update_fields=['active_organization'])

    request.advanced_json = {
        'email': user.email, 'allow_newsletters': user.allow_newsletters,
        'update-notifications': 1, 'new-user': 1
    }
    redirect_url = next_page if next_page else reverse('projects:project-index')
    auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect(redirect_url)


def proceed_registration(request, user_form, organization_form, next_page):
    """ Register a new user for POST user_signup
    """
    # save user to db
    save_user = load_func(settings.SAVE_USER)
    response = save_user(request, next_page, user_form)

    return response


def send_email_verification(user, domain_verify=None):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator._make_token_with_timestamp(
        user,
        int((datetime.now() + timedelta(minutes=24 * 60 * 3)).timestamp())
    )

    if not domain_verify:
        verify_link = f'{settings.BASE_BACKEND_URL}/api/user/email-verify/{user.id}/{token}'
    else:
        verify_link = f'{domain_verify}/api/user/email-verify/{user.id}/{token}'

    html_file_path = './aixblock_core/templates/mail/email-verification.html'

    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # notify_reponse = ServiceSendEmail(DOCKER_API)
    if user.first_name:
        send_to = user.first_name
    else:
        send_to = user.username if user.username else user.email

    html_content = html_content.replace('[user]', f'{send_to}')
    html_content = html_content.replace('[link]', f'{verify_link}')

    data = {
        "subject": "Welcome to AIxBlock - Verify your email",
        "from": "noreply@aixblock.io",
        "to": [f"{user.email}"],
        "html": html_content,
    }

    docket_api = "tcp://69.197.168.145:4243"
    host_name = MAIL_SERVER

    email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
    email_thread.start()


def generate_username():
    characters = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(characters) for _ in range(10))
    return username


def is_valid_email(email):
    email: str = email.strip().lower()

    if email.endswith("@uniphore.com"):
        return {
            "is_valid": True,
            "has_error": False,
        }

    is_valid = False
    has_error = False
    res = requests.get(
        "https://emailverification.whoisxmlapi.com/api/v3?"
        "apiKey=at_NM7qzSOximxvsLDco04honcmooM7d"
        "&emailAddress=" + email +
        "&outputFormat=JSON"
    )

    if res.status_code == 200:
        try:
            # Boolean values of the response is in string format, not actually boolean
            data = res.json()

            is_valid = (
                    # Lets you know if there are any syntax errors in the email address.
                    data['formatCheck'] == 'true'
                    # Checks if the email address exists and can receive emails by using SMTP connection
                    # and email-sending emulation techniques.
                    and data['smtpCheck'] == 'true'
                    # Ensures that the domain in the email address, eg: gmail.com, is a valid domain.
                    and data['dnsCheck'] == 'true'
                    # Tells you whether or not the email address is disposable (created via a service
                    # like Mailinator)
                    and data['disposableCheck'] == 'false'
            )
        except Exception as e:
            logging.error(e)
            has_error = True
    else:
        has_error = True

    return {
        "is_valid": is_valid,
        "has_error": has_error,
    }


def get_list_user_jupyterhub(token):
    url = f"{HOST_JUPYTERHUB}/hub/api/users/admin/tokens"
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}'
        }
    
    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Data received:", data)
    else:
        print(f"Failed to get data. Status code: {response.status_code}")
        print("Response content:", response.text)

def update_token_admin(token):
    os.environ['ADMIN_JUPYTERHUB_TOKEN'] = token

def create_user(user, token=None):
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}'
        }
    
    url = f"{HOST_JUPYTERHUB}/services/wow-ai-api/create_user/{user}"
    response = requests.request("POST", url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Data received:", data)
    else:
        print(f"Failed to get data. Status code: {response.status_code}")
        print("Response content:", response.text)

    # url = f"{HOST_JUPYTERHUB}/hub/api/users"
    # payload = json.dumps({
    #     "usernames": [
    #         f"{user}"
    #     ],
    #     "admin": False
    #     })
    
    # response = requests.request("POST", url, headers=headers, data=payload)
    # if response.status_code == 200:
    #     data = response.json()
    #     print("Data received:", data)
    # else:
    #     print(f"Failed to get data. Status code: {response.status_code}")
    #     print("Response content:", response.text)

def create_folder(user, folder, token=None):
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}'
        }
    
    url = f"{HOST_JUPYTERHUB}/services/wow-ai-api/create_folder/{user}/{folder}"
    response = requests.request("POST", url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Data received:", data)
    else:
        print(f"Failed to get data. Status code: {response.status_code}")
        print("Response content:", response.text)

def start_server_jp(user, token):
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}'
        }
    
    url = f"{HOST_JUPYTERHUB}/hub/api/users/{user}/server"
    response = requests.request("POST", url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Data received:", data)
    else:
        print(f"Failed to get data. Status code: {response.status_code}")
        print("Response content:", response.text)
