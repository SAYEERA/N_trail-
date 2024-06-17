from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import (home, browse, signup, my_projects, logout_view, import_experiment,
                    all_projects, all_locations, project_database, add_project, add_experiment, show_experiments,
                    add_location, show_treatments,upload_experiment_file,download_file,save_plot_data)


urlpatterns = [
    path('', home, name='home'),
    path('browse/', browse, name='browse'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('locations/', all_locations, name='all_locations'),
    path('add_location/', add_location, name='add_location'),
    path('logout/', logout_view, name='logout'),
    path('browse/my_projects/', my_projects, name='my_projects'),
    path('browse/all_projects/', all_projects, name='all_projects'),
    path('browse/locations/', all_locations, name='locations'),
    path('project_database/', project_database, name='project_database'),
    path('add_project/', add_project, name='add_project'),
    path('add_experiment/', add_experiment, name='add_experiment'),
    path('projects/<str:project_id>/experiments/', show_experiments, name='show_experiments'),
    path('show_treatments/<str:experiment_id>/', show_treatments, name='show_treatments'),
    path('import_experiment/', import_experiment, name='import_experiment'),
    path('experiments/<str:experiment_id>/treatments/', show_treatments, name='show_treatments'),
    path('upload_experiment_file/<str:experiment_id>/<str:file_field>/', upload_experiment_file, name='upload_experiment_file'),
    # path('experiment/<int:experiment_id>/save_plot/', save_plot, name='save_plot'),
    # path('save_plot/', save_plot, name='save_plot'),
    path('treatment/<str:treatment_id>/save_plot_data/', save_plot_data, name='save_plot_data'),
    path('download/<path:file_path>/', download_file, name='download_file'),
]



if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)