# N_trail_dashboard/urls.py

from django.urls import path,include
from django.contrib.auth import views as auth_views 
from .views import home, browse, signup,my_projects,logout_view,import_experiment, all_projects,all_locations,project_database,add_project,add_experiment,show_experiments,add_location, show_treatments

urlpatterns = [
    path('', home, name='home'),
    path('browse/', browse, name='browse'),
    path('accounts/', include('django.contrib.auth.urls')),  
     path('signup/',signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('locations/', all_locations, name='all_locations'),
    path('add_location/', add_location, name='add_location'),
    path('logout/',logout_view, name='logout'),
    path('browse/my_projects/', my_projects, name='my_projects'),
    path('browse/all_projects/', all_projects, name='all_projects'),
    path('browse/locations/', all_locations, name='locations'),
    path('project_database/', project_database, name='project_database'),
    path('add_project/', add_project, name='add_project'),  # Update this line
    path('add_experiment/', add_experiment, name='add_experiment'),  # Update this line
    path('projects/<str:project_id>/experiments/', show_experiments, name='show_experiments'),
   
    path('show_treatments/<str:experiment_id>/', show_treatments, name='show_treatments'),
    path('import_experiment/', import_experiment, name='import_experiment'),
    path('experiments/<str:experiment_id>/treatments/', show_treatments, name='show_treatments'),
]
