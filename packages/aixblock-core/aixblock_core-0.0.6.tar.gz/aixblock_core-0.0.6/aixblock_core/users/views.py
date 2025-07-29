"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import PermissionDenied
import pandas as pd
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from users import forms
from core.utils.common import load_func
from core.middleware import enforce_csrf_checks
from users.functions import proceed_registration, generate_username
from organizations.models import Organization
from organizations.forms import OrganizationSignupForm

logger = logging.getLogger()


@login_required
def logout(request):
    auth.logout(request)
    if settings.HOSTNAME:
        redirect_url = settings.HOSTNAME
        if not redirect_url.endswith('/'):
            redirect_url += '/'
        return redirect(redirect_url)
    return redirect('/')


@enforce_csrf_checks
def user_signup(request):
    """ Sign up page
    """
    user = request.user
    next_page = request.GET.get('next')
    token = request.GET.get('token')
    next_page = next_page if next_page else reverse('projects:project-index')
    user_form = forms.UserSignupForm()
    organization_form = OrganizationSignupForm()

    if user.is_authenticated:
        return redirect(next_page)

    # make a new user
    if request.method == 'POST':
        organization = Organization.objects.first()
        if settings.DISABLE_SIGNUP_WITHOUT_LINK is True:
            if not(token and organization and token == organization.token):
                raise PermissionDenied()
        else:
            if token and organization and token != organization.token:
                raise PermissionDenied()

        user_form = forms.UserSignupForm(request.POST)
        organization_form = OrganizationSignupForm(request.POST)

        if user_form.is_valid():
            redirect_response = proceed_registration(request, user_form, organization_form, next_page)
            if redirect_response:
                return redirect_response

    return render(request, 'users/user_signup.html', {
        'user_form': user_form,
        'organization_form': organization_form,
        'next': next_page,
        'token': token,
    })


@enforce_csrf_checks
def user_login(request):
    """ Login page
    """
    user = request.user
    next_page = request.GET.get('next')
    next_page = next_page if next_page else reverse('projects:project-index')
    is_restful = request.META['HTTP_ACCEPT'] == "application/json"

    if user.is_authenticated:
        if is_restful:
            return JsonResponse({"status": 200, "redirect": next_page})
        else:
            return redirect(next_page)

    if request.method == 'POST':
        login_form = load_func(settings.USER_LOGIN_FORM)
        form = login_form(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user']
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            try:
                if user.id not in user.active_organization.active_members.values_list("user_id", flat=True):
                    user.active_organization = None
                # user is organization member
                if user.active_organization is None:
                    org_pk = Organization.find_by_user(user).pk
                    user.active_organization_id = org_pk
                    user.active_organization = None
                    user.save(update_fields=['active_organization'])
            except Exception as e:
                print(e)

            if not user.username or len(user.username) == 0:
                user.username = generate_username()
                user.save()

            if is_restful:
                return JsonResponse({"status": 200, "redirect": next_page})
            else:
                return redirect(next_page)
        else:
            return JsonResponse({"status": 400, "errors": form.errors}, status=400)

    if is_restful:
        return Http404()
    else:
        return render(request, 'users/user_login.html')


@enforce_csrf_checks
def user_reset_password(request):
    """ Reset Password page
    """
    is_restful = request.META['HTTP_ACCEPT'] == "application/json"

    if is_restful:
        return Http404()
    else:
        return render(request, 'users/user_reset_password.html')

@login_required
def user_account(request):
    user = request.user

    if user.active_organization is None and 'organization_pk' not in request.session:
        return redirect(reverse('main'))

    form = forms.UserProfileForm(instance=user)
    token = Token.objects.get(user=user)

    if request.method == 'POST':
        form = forms.UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse('user-account'))
        
    return render(request, 'users/user_account.html', {
        'settings': settings,
        'user': user,
        'user_profile_form': form,
        'token': token
    })


@login_required
def user_bulk(request):
    user = request.user
    #csv bulk
    # tonyshark,tonyshark@yahoo.com,password,1
    # tonyshark1,tonyshark1@yahoo.com,password,1

    # if user.active_organization is None and 'organization_pk' not in request.session:
    #     return redirect(reverse('main'))

    form = forms.UserProfileForm(instance=user)
    token = Token.objects.get(user=user)
    import os
    if request.method == 'POST':
        data = request.POST
        full_path = os.path.join(settings.MEDIA_ROOT)
       
        files = request.FILES.items()
        print(f"files:{files}")
        for filename, file in files:
            print(f"file:{file}")
            full_path = os.path.join(os.getcwd(),file.name)
            print(f"full_path:{full_path}")
            print(f"filename:{file.name}")
            dest = open(full_path, 'wb')
            if file.multiple_chunks:
                for c in file.chunks():
                    dest.write(c)
            else:
                dest.write(file.read())
            dest.close()
        
            # filename = os.path.basename(full_path)
            csv_df = pd.read_csv(full_path,sep=',').fillna('')
            row_iter = csv_df.iterrows()
            print(row_iter)
            # from django.contrib.auth.models import User
            from users.models import User
            for index, row in row_iter:
                user = User.objects.create_user(username=row[0],
                                                email=row[1].lower(),
                                                password=row[2],
                                                is_staff=True,
                                                is_superuser=False,
                                                is_qa=False,
                                                is_qc=False)
                team_ids = [row[3]] 
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
        # return redirect(reverse('admin:users_user_changelist'))
        
    return render(request, 'users/user_bulk.html', {
        'settings': settings,
        'user': user,
        'user_profile_form': form,
        'token': token
    })


@login_required
@require_http_methods(["GET"])
def notebook(request):
    from projects.models import Project
    from core.permissions import permission_org

    username = request.user.username
    project_id = request.GET.get('project_id')
    project_workspace = f"project-{project_id}"

    project = Project.objects.get(id=project_id)
    
    if not permission_org(request.user, project):
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    if settings.NOTEBOOK_URL is None:
        url = request.build_absolute_uri("/")
        up = urlparse(url)
        up = up._replace(netloc=up.netloc.replace(str(up.port), "8100"))
        url = up.geturl()
    else:
        url = settings.NOTEBOOK_URL

    if "http" not in url:
        url = "http://" + url

    url = url.rstrip('/')

    try:
        from .functions import create_folder
        from users.functions import create_user, create_folder, start_server_jp
        if username == 'admin' or 'admin@wow-ai.com' in request.user.email:
            create_user(username)
            start_server_jp(username, settings.NOTEBOOK_TOKEN)
            create_folder(username, project_workspace)

        else:
            username = request.user.email
            create_user(request.user.email)
            start_server_jp(request.user.email, settings.NOTEBOOK_TOKEN)
            create_folder(request.user.email, project_workspace)

        # requests.post(
        #     url + "services/wow-ai-api/create_user/" + username,
        #     headers={"Authorization": "Bearer " + settings.NOTEBOOK_TOKEN},
        # )
    except Exception as e:
        print(e)
        # return HttpResponseNotFound(f'{e}')

    # email.xyz@gmail.com -> email__dot__xyz__at__gmail__dot__com
    return HttpResponseRedirect(url + "/user/" + username + "/lab/workspaces/auto-d/tree/" + f'{project_workspace}')
