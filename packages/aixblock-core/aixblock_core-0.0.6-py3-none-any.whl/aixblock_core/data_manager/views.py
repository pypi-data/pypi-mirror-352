"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.utils.common import find_editor_files
from core.version import info


@login_required
def task_page(request, pk):
    response = {
        'version': "aixblock:2.1.2"
    }
    response.update(find_editor_files())
    return render(request, 'base.html', response)
