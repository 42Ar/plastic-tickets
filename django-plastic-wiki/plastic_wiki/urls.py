from django.urls import path

from . import views

urlpatterns = [
    path('', views.wiki_index_view, name='plastic_tickets_index'),
]
