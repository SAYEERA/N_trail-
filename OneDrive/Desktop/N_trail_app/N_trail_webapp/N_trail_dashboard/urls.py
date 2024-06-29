from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import (home, signup, my_projects, logout_view, import_experiment,download_csv, upload_csv,
                    all_projects, all_locations,upload_treatment_csv, project_database, add_project, add_experiment, show_experiments,
                    add_location,save_consolidated_plots, get_column_values, show_treatments,upload_experiment_file,download_file,save_plot_data,get_plot_data, project_experiments,  show_treatments_and_plots)


urlpatterns = [
    path('', home, name='home'),
    # path('browse/', browse, name='browse'),
    path('accounts/', include('django.contrib.auth.urls')),
      
    path('experiment/<str:experiment_id>/upload_treatment_csv/', upload_treatment_csv, name='upload_treatment_csv'),
    path('save_consolidated_plots/', save_consolidated_plots, name='save_consolidated_plots'),
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
    path('projects/<str:project_id>/experiments/list/', project_experiments, name='project_experiments'),
    path('projects/<str:project_id>/experiments/', show_experiments, name='show_experiments'),
    path('show_treatments/<str:experiment_id>/', show_treatments, name='show_treatments'),
    path('import_experiment/', import_experiment, name='import_experiment'),
    path('experiments/<str:experiment_id>/treatments/', show_treatments, name='show_treatments'),
    path('upload_experiment_file/<str:experiment_id>/<str:file_field>/', upload_experiment_file, name='upload_experiment_file'),
    path('download_file/<path:file_path>/', download_file, name='download_file'),
    path('treatment/<str:treatment_id>/save_plot_data/', save_plot_data, name='save_plot_data'),
    path('download/<path:file_path>/', download_file, name='download_file'),
     path('get_column_values/', get_column_values, name='get_column_values'),
    path('treatment/<str:treatment_id>/get_plot_data/', get_plot_data, name='get_plot_data'),
    path('treatment/<str:treatment_id>/download_csv/', download_csv, name='download_csv'),  # Updated URL for downloading CSV
    path('treatment/<str:treatment_id>/upload_csv/', upload_csv, name='upload_csv'),  # Updated URL for uploading CSV
    path('experiment/<str:experiment_id>/treatments_plots/', show_treatments_and_plots, name='show_treatments_and_plots'),
]



if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)