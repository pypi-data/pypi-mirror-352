"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required
def organization_people_list(request):
    return render(request, 'organizations/people_list.html')

@login_required
def simple_view(request):
    return render(request, 'organizations/people_list.html')
@login_required
def organization_export_report(request):
    if request.method == 'POST':
        data = request.POST
        print(request.GET)
        print(f"organization_export_report:{data}")
        # return redirect(reverse('admin:organizations_organization_export_report', kwargs={'project_id':0,'role':'','org_id':0}))
    return render(request, 'organizations/export_report.html',{'pk': 1})