from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from . import models


def wiki_index_view(request: HttpRequest) -> HttpResponse:
    sections = models.WikiSection.get_all()

    return render(request, 'plastic_wiki/index.html',
                  context={'sections': sections})


def section_index_view(request: HttpRequest) -> HttpResponse:
    return render('Wiki index')
