from pathlib import Path
from typing import List
import json

from django.contrib.auth.models import User
from django.contrib.auth.views import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from . import models


def tickets_index_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'plastic_tickets/overview.html')


def get_cached_filenames_for_user(user: User) -> List[str]:
    cached_dir = Path('cached_files/', user.username)
    cached_dir.mkdir(parents=True, exist_ok=True)

    files: List[str] = []
    for file in cached_dir.glob('*'):
        files.append(file.name)

    return files


@login_required
def new_ticket_view(request: HttpRequest, active_file='') -> HttpResponse:
    if request.method == 'POST':
        print(request.POST)

    files = get_cached_filenames_for_user(request.user)

    if not active_file and len(files) > 0:
        active_file = files[0]

    tree = models.get_option_tree()
    
    js_data = json.dumps(tree, default=lambda o: o.to_json())

    return render(request, 'plastic_tickets/new_ticket.html',
                  {
                      'files': files, 'active_file': active_file,
                      'js_data': js_data,
                  })
