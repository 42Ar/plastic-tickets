import json
from pathlib import Path
from typing import List

from django.contrib.auth.models import User
from django.contrib.auth.views import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from . import models, forms


def tickets_index_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'plastic_tickets/overview.html')


def get_cached_dir(user: User) -> Path:
    return Path('cached_files/', user.username)


def get_cached_filenames_for_user(user: User) -> List[Path]:
    cached_dir = get_cached_dir(user)
    cached_dir.mkdir(parents=True, exist_ok=True)

    files: List[Path] = []
    for file in cached_dir.glob('*'):
        files.append(file)

    return files


def get_configured_filenames_for_user(user: User) -> List[Path]:
    return [Path(f.config.file) for f in
            models.CachedPrintConfig.objects.filter(user=user).all()]


@login_required
def new_ticket_view(request: HttpRequest, active_file='') -> HttpResponse:
    files = get_cached_filenames_for_user(request.user)

    if not active_file and len(files) > 0:
        active_file = files[0]
    else:
        active_file = get_cached_dir(request.user).joinpath(active_file)

    tree = models.get_option_tree()

    js_data = json.dumps(tree, default=lambda o: o.to_json())

    configured_files = get_configured_filenames_for_user(request.user)

    if request.method == 'POST':
        if forms.cache_config(active_file, request.user, request.POST):
            configured_files.append(active_file)
            unconfigured_file = next((f for f in files
                                      if f not in configured_files), None)
            if unconfigured_file is not None:
                return redirect('plastic_tickets_new_with_file_view',
                                active_file=unconfigured_file.name)

    return render(request, 'plastic_tickets/new_ticket.html',
                  {
                      'files': files, 'active_file': Path(active_file),
                      'js_data': js_data,
                      'configured_files': configured_files,
                  })
