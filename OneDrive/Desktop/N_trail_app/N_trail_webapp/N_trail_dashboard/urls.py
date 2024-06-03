# N_trail_dashboard/urls.py

from django.urls import path
from .views import home, browse, my_projects, all_projects,locations,data_analysis,add_project,add_experiment,show_experiments, show_treatments

urlpatterns = [
    path('', home, name='home'),
    path('browse/', browse, name='browse'),
    path('browse/my_projects/', my_projects, name='my_projects'),
    path('browse/all_projects/', all_projects, name='all_projects'),
    path('browse/locations/', locations, name='locations'),
    path('data_analysis/', data_analysis, name='data_analysis'),
    path('add_project/', add_project, name='add_project'),  # Update this line
    path('add_experiment/', add_experiment, name='add_experiment'),  # Update this line
    path('projects/<str:project_id>/experiments/', show_experiments, name='show_experiments'),
   
    path('show_treatments/<str:experiment_id>/', show_treatments, name='show_treatments'),

    path('experiments/<str:experiment_id>/treatments/', show_treatments, name='show_treatments'),
]
