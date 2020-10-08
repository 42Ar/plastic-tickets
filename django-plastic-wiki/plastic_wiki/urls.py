from django.urls import path

from . import views

urlpatterns = [
    path('', views.wiki_index_view, name='wiki_index'),
    path('<section>/', views.section_index_view,
         name='plastic_wiki_section_view')
]
