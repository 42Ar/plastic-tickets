import json
from pathlib import Path

from django.contrib.auth.views import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from . import models, forms, util


def tickets_index_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'plastic_tickets/overview.html')


@login_required
def new_ticket_view(request: HttpRequest, active_file='') -> HttpResponse:
    files = util.get_cached_filenames_for_user(request.user)

    if not active_file and len(files) > 0:
        active_file = files[0]
    else:
        active_file = util.get_cached_dir(request.user).joinpath(active_file)

    tree = models.get_option_tree()

    js_data = json.dumps(tree, default=lambda o: o.to_json())

    configured_files = util.get_configured_filenames_for_user(request.user)

    if request.method == 'POST':
        if request.POST.get('config_form') is not None:
            if forms.cache_config(active_file, request.user, request.POST):
                configured_files.append(active_file)
                unconfigured_file = next((f for f in files
                                          if f not in configured_files), None)
                if unconfigured_file is not None:
                    return redirect('plastic_tickets_new_with_file_view',
                                    active_file=unconfigured_file.name)
        elif request.POST.get('file_upload') is not None:
            files = request.FILES.getlist('file[]')
            if files is not None:
                forms.cache_files(request.user, files)
                return redirect('plastic_tickets_new_view')
        elif request.POST.get('file_delete') is not None:
            util.delete_all_cached_files_for_user(request.user)
            return redirect('plastic_tickets_new_view')

    return render(request, 'plastic_tickets/new_ticket.html',
                  {
                      'files': files, 'active_file': Path(active_file),
                      'js_data': js_data,
                      'configured_files': configured_files,
                      'fully_configured': set(configured_files) == set(files),
                  })
