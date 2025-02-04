from django.shortcuts import render,get_object_or_404,redirect
from .models import Project, Location, Experiment, Treatment, Plot
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound 
from itertools import product
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import random
import matplotlib.pyplot as plt
import json
import matplotlib.pyplot as plt
import io
import base64
import os
from django.conf import settings 
from django.db import transaction
import logging
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth import login, logout 
from .forms import LocationForm
import itertools
import csv
from django.db.models import Max
import random
from django.contrib.auth.models import User
logger = logging.getLogger(__name__)

def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

# def home(request):
#     return render(request, 'home.html')

def home(request):
    projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects})

    
@login_required
def my_projects(request):
    crop_choices = Project.CROP_CHOICES
    users = User.objects.all()  # Fetch all users to populate the project editors dropdown
    logged_in_user_email = request.user.email  # Get the logged-in user's email

    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(Project_Editors__icontains=logged_in_user_email)

    # Filter out projects without a valid Project_ID and log them
    valid_projects = []
    for project in projects:
        if project.Project_ID:
            valid_projects.append(project)
        else:
            logger.error(f"Project with missing Project_ID: {project}")

    context = {
        'projects': valid_projects,
        'crop_choices': crop_choices,
        'users': users,
    }

    return render(request, 'my_projects.html', context)



@csrf_exempt
def project_experiments(request, project_id):
    project = get_object_or_404(Project, Project_ID=project_id)
    experiment_filter_value = request.GET.get('experiment_filter', '')
    if experiment_filter_value:
        experiments = Experiment.objects.filter(Project_ID=project, Experiment_ID__icontains=experiment_filter_value)
    else:
        experiments = Experiment.objects.filter(Project_ID=project)
    return render(request, 'project_experiments.html', {'project': project, 'experiments': experiments})

def show_experiments(request, project_id):
    # location_choices = Experiment.LOCATION_CHOICES
    location_choices = Location.objects.all()  # Fetch all locations
    project = get_object_or_404(Project, pk=project_id)
    experiments = Experiment.objects.filter(Project_ID=project)
    file_types = [
        'Yield_Map', 'Soil_Sample', 'Sonic_sensor', 'GCP',
        'RAWUAV', 'Orthomosic_UAV', 'DSM_UAV', 'Orthomosic_SAT',
        'DSM_SAT', 'VI_1', 'VI_2', 'VI_3'
    ]

    context = {
        'experiments': experiments, 
        'location_choices': location_choices,
        'project': project,
        'file_types': file_types,  # Add file_types to the context
    }


    return render(request, 'show_experiments.html',context )

from django.shortcuts import get_object_or_404, render
from .models import Experiment, Treatment, Plot

def show_treatments_and_plots(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    treatments = Treatment.objects.filter(Experiment_ID=experiment)
    
    # Sort treatments by numeric part of Treatment_ID
    sorted_treatments = sorted(treatments, key=lambda t: int(t.Treatment_ID.split('_T')[1]))

    plot_data = {}
    for treatment in sorted_treatments:  # Use sorted_treatments here
        plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
        for plot in plots:
            plot_data[(treatment.Treatment_ID, plot.Replication_ID)] = plot.Plot_ID

    context = {
        'experiment': experiment,
        'treatments': sorted_treatments,  # Pass sorted_treatments to the context
        'plot_data': plot_data
    }
    return render(request, 'treatments_and_plots.html', context)




@login_required
def all_projects(request):
    public_projects = Project.objects.select_related('User_ID')
    # public_projects = Project.objects.select_related('User_ID').filter(View_Type='private')
    return render(request, 'all_projects.html', {'projects': public_projects})

def all_locations(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_locations')
    else:
        form = LocationForm()

    locations = Location.objects.all()
    return render(request, 'locations.html', {'locations': locations, 'form': form})





@csrf_exempt
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save()
            return JsonResponse({'success': True, 'location_id': location.Location_ID})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
@login_required
def import_experiment(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return JsonResponse({'success': False, 'error': 'No file uploaded'})

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            experiments = []

            for row in reader:
                try:
                    project_id = row['PROJECT ID']
                    location_id = row['Location ID']
                    experiment_id = row['Experiment ID']
                    year = row['Year']
                    interaction_1_count = int(row['Interaction_1_count'])
                    interaction_2_count = int(row['Interaction_2_count'])
                    interaction_3_count = int(row['Interaction_3_count'])
                    interaction_1_value = row['Interaction_1_Value']
                    interaction_2_value = row['Interaction_2_Value']
                    interaction_3_value = row['Interaction_3_Value']
                    yield_map = row['Yield_Map']
                    soil_sample = row['Soil_Sample']
                    sonic_sensor = row['Sonic_sensor']
                    gcp = row['GCP']
                    rawuav = row['RAW UAV']
                    orthomosic_uav = row['Orthomosic_UAV']
                    dsm_uav = row['DSM_UAV']
                    orthomosic_sat = row['Orthomosic_SAT']
                    dsm_sat = row['DSM_SAT']
                    vi_1 = row['VI_1']
                    vi_2 = row['VI_2']
                    vi_3 = row['VI_3']
                    metadata = row['MetaData']

                    project = get_object_or_404(Project, pk=project_id)
                    location, created = Location.objects.get_or_create(Location_ID=location_id)

                    experiment = Experiment(
                        Experiment_ID=experiment_id,
                        Project_ID=project,
                        Location_ID=location,
                        Year=year,
                        Interaction_1_count=interaction_1_count,
                        Interaction_2_count=interaction_2_count,
                        Interaction_3_count=interaction_3_count,
                        Interaction_1_value=interaction_1_value,
                        Interaction_2_value=interaction_2_value,
                        Interaction_3_value=interaction_3_value,
                        Yield_Map=yield_map,
                        Soil_Sample=soil_sample,
                        Sonic_sensor=sonic_sensor,
                        GCP=gcp,
                        RAWUAV=rawuav,
                        Orthomosic_UAV=orthomosic_uav,
                        DSM_UAV=dsm_uav,
                        Orthomosic_SAT=orthomosic_sat,
                        DSM_SAT=dsm_sat,
                        VI_1=vi_1,
                        VI_2=vi_2,
                        VI_3=vi_3,
                        MetaData=metadata
                    )
                    experiments.append(experiment)
                except KeyError as e:
                    return JsonResponse({'success': False, 'error': f'Missing field in CSV: {str(e)}'})

            Experiment.objects.bulk_create(experiments)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



@csrf_exempt
@login_required
def add_project(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('Project_ID')
            
            # Check if the project ID already exists
            if Project.objects.filter(Project_ID=project_id).exists():
                return JsonResponse({'success': False, 'error': 'Project ID already exists.'})

            user_id = request.user.id
            # start_year = request.POST.get('Start_year')
            interactions_count = request.POST.get('Interactions_count')
            interaction_1 = request.POST.get('Interaction_1')
            interaction_2 = request.POST.get('Interaction_2')
            interaction_3 = request.POST.get('Interaction_3')
            crop = request.POST.get('Crop')
            # no_of_years = request.POST.get('No_of_
            project_editors = request.POST.get('Project_Editors')
            funding_source = request.POST.get('Funding_Source')
            metadata = request.POST.get('MetaData')
            view_type = request.POST.get('View_Type')

            # Create the project
            project = Project.objects.create(
                Project_ID=project_id,
                User_ID_id=user_id,
                # Start_year=start_year,
                Interactions_count=interactions_count,
                Interaction_1=interaction_1,
                Interaction_2=interaction_2,
                Interaction_3=interaction_3,
                Crop=crop,
                # No_of_Year=no_of_years,
                Project_Editors=project_editors,
                Funding_Source=funding_source,
                MetaData=metadata,
                View_Type=view_type
            )

            # Create folder and save project details as a .txt file
            # base_dir = os.path.join(settings.BASE_DIR, 'N_trail_folder')
            # base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')
            base_dir = os.path.join(settings.MEDIA_ROOT, 'N_trail_folder')


            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            project_dir = os.path.join(base_dir, project_id)
            os.makedirs(project_dir, exist_ok=True)

            print(f"Base directory: {base_dir}")
            print(f"Project directory: {project_dir}")

            file_path = os.path.join(project_dir, 'Meta_data.txt')
            with open(file_path, 'w') as file:
                file.write(f'Project ID: {project_id}\n')
                file.write(f'User ID: {user_id}\n')
                # file.write(f'Start Year: {start_year}\n')
                file.write(f'Interactions Count: {interactions_count}\n')
                file.write(f'Interaction 1: {interaction_1}\n')
                file.write(f'Interaction 2: {interaction_2}\n')
                file.write(f'Interaction 3: {interaction_3}\n')
                file.write(f'Crop: {crop}\n')
                # file.write(f'Number of Years: {no_of_years}\n')
                file.write(f'Project Editors: {project_editors}\n')
                file.write(f'Funding Source: {funding_source}\n')
                file.write(f'Metadata: {metadata}\n')
                file.write(f'View Type: {view_type}\n')

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def download_file(request, file_path):
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return HttpResponseNotFound("File not found")


@login_required
def add_experiment(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('Project_ID')
            experiment_id = request.POST.get('Experiment_ID')
            year = request.POST.get('Year')
            location_id = request.POST.get('Location_ID')
            interaction_1_count = int(request.POST.get('Interaction_1_count', '0') or '0')
            interaction_2_count = int(request.POST.get('Interaction_2_count', '0') or '0')
            interaction_3_count = int(request.POST.get('Interaction_3_count', '0') or '0')
            metadata = request.POST.get('MetaData')
            no_of_replicates = int(request.POST.get('No_of_Replicates', '1'))

            project = get_object_or_404(Project, pk=project_id)

            if location_id == 'other':
                location_data = {
                    'Location_ID': request.POST.get('New_Location_ID'),
                    'State': request.POST.get('New_State'),
                    'County': request.POST.get('New_County'),
                    'Owner': request.POST.get('New_Owner'),
                    'Latitude': request.POST.get('New_Latitude'),
                    'Longitude': request.POST.get('New_Longitude'),
                    'Contact': request.POST.get('New_Contact'),
                    'MetaData': request.POST.get('New_MetaData')
                }
                location = Location.objects.create(**location_data)
                location_id = location.Location_ID
            else:
                location = get_object_or_404(Location, pk=location_id)

            experiment = Experiment.objects.create(
                Experiment_ID=experiment_id,
                Project_ID=project,
                Location_ID=location,
                Year=year,
                Interaction_1_count=interaction_1_count,
                Interaction_2_count=interaction_2_count,
                Interaction_3_count=interaction_3_count,
                MetaData=metadata
            )

            interaction_1_values = [request.POST.get(f'Interaction_1_{i}', 'NA') for i in range(1, interaction_1_count + 1)]
            interaction_2_values = [request.POST.get(f'Interaction_2_{i}', 'NA') for i in range(1, interaction_2_count + 1)]
            interaction_3_values = [request.POST.get(f'Interaction_3_{i}', 'NA') for i in range(1, interaction_3_count + 1)]

            experiment.Interaction_1_value = ','.join(interaction_1_values)
            experiment.Interaction_2_value = ','.join(interaction_2_values)
            experiment.Interaction_3_value = ','.join(interaction_3_values)

            experiment.save()
            base_dir = os.path.join(settings.MEDIA_ROOT, 'N_trail_folder')

            # base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')
            project_folder = os.path.join(base_dir, project.Project_ID)
            experiment_folder = os.path.join(project_folder, experiment_id)
            os.makedirs(experiment_folder, exist_ok=True)

            file_path = os.path.join(experiment_folder, 'Meta-data.txt')
            with open(file_path, 'w') as file:
                file.write(f'Experiment ID: {experiment_id}\n')
                file.write(f'Project ID: {project_id}\n')
                file.write(f'Location ID: {location_id}\n')
                file.write(f'Year: {year}\n')
                file.write(f'Interaction 1 Count: {interaction_1_count}\n')
                file.write(f'Interaction 1 Value: {experiment.Interaction_1_value}\n')
                file.write(f'Interaction 2 Count: {interaction_2_count}\n')
                file.write(f'Interaction 2 Value: {experiment.Interaction_2_value}\n')
                file.write(f'Interaction 3 Count: {interaction_3_count}\n')
                file.write(f'Interaction 3 Value: {experiment.Interaction_3_value}\n')
                file.write(f'Metadata: {metadata}\n')
            
            # Generate treatments

            interaction_1_count = len(interaction_1_values)
            interaction_2_count = len(interaction_2_values)
            interaction_3_count = len(interaction_3_values)
            
            # Organize Interactions
            interactions = [interaction_1_values, interaction_2_values, interaction_3_values]
            valid_interactions = [i for i in interactions if i]  # Filter out empty lists 

            #generate combinations
            interaction_combinations = list(product(*valid_interactions))

            treatments = []
            treatment_id_prefix = f"{experiment_id}_T"

           # Generate Treatments
            for idx, combination in enumerate(interaction_combinations):
                treatment_id = f"{treatment_id_prefix}{idx + 1}"
                treatments.append(Treatment(
                    Treatment_ID=treatment_id,
                    Experiment_ID=experiment,
                    Interaction_1_Value=combination[0] if len(combination) > 0 else '',
                    Interaction_2_Value=combination[1] if len(combination) > 1 else '',
                    Interaction_3_Value=combination[2] if len(combination) > 2 else '',
                    No_of_Replication=no_of_replicates,
                    MetaData=metadata
                ))
             # Sort treatments by the numeric part of the Treatment_ID
            treatments.sort(key=lambda x: int(x.Treatment_ID.split('_T')[1]))
            # Bulk Create Treatments
            Treatment.objects.bulk_create(treatments)

            return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID, 'no_of_replicates': no_of_replicates})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def download_file(request, file_path):
    # Log the received file path for debugging
    # print(f"Requested file path: {file_path}")

    # Construct the full file path
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    # print(f"Full file path: {full_file_path}")

    if os.path.exists(full_file_path):
        with open(full_file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(full_file_path)}"'
            return response
    else:
        # print(f"File not found: {full_file_path}")
        return HttpResponseNotFound("File not found")

@login_required
@csrf_exempt
def upload_experiment_file(request, experiment_id, file_field):
    if request.method == 'POST':
        experiment = get_object_or_404(Experiment, pk=experiment_id)
        files = request.FILES.getlist('files')
        if files:
            try:
                project_dir = os.path.join(settings.MEDIA_ROOT, 'N_trail_folder', str(experiment.Project_ID.Project_ID))
                experiment_dir = os.path.join(project_dir, str(experiment.Experiment_ID))
                os.makedirs(experiment_dir, exist_ok=True)
                
                file_paths = []
                for file in files:
                    user_provided_name = file.name
                    file_path = os.path.join(experiment_dir, user_provided_name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    file_paths.append(os.path.relpath(file_path, settings.MEDIA_ROOT))
                
                existing_files = getattr(experiment, file_field, None)
                if existing_files is None:
                    existing_files = []
                elif isinstance(existing_files, str):
                    existing_files = [existing_files]
                
                existing_files.extend(file_paths)
                setattr(experiment, file_field, existing_files)
                experiment.save()

                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': 'No files uploaded'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
@csrf_exempt
def upload_csv(request, experiment_id):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)

        try:
            with transaction.atomic():
                for row in reader:
                    if row[0] != "Treatment ID":  # Skip the header
                        treatment_id, replication_id, plot_id = row
                        Plot.objects.update_or_create(
                            Treatment_ID=Treatment.objects.get(Treatment_ID=treatment_id),
                            Replication_ID=int(replication_id),
                            defaults={'Plot_ID': plot_id}
                        )
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error uploading plot data: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def download_csv(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    treatments = Treatment.objects.filter(Experiment_ID=experiment_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="plot_table_{experiment_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Treatment ID', 'Replication ID', 'Plot ID'])

    for treatment in treatments:
        for rep in range(1, int(treatment.No_of_Replication) + 1):
            writer.writerow([str(treatment.Treatment_ID), str(rep), ''])

    return response



@login_required
def get_plot_data(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    treatments = Treatment.objects.filter(Experiment_ID=experiment)
    plot_data = {}

    for treatment in treatments:
        plots = treatment.plot_set.all()
        plot_data[treatment.Treatment_ID] = {
            'interaction_1_value': treatment.Interaction_1_Value,
            'interaction_2_value': treatment.Interaction_2_Value,
            'units': plots[0].Units if plots else '',
            'plots': [{'replication_id': plot.Replication_ID, 'plot_id': plot.Plot_ID, 'yield': plot.Yield} for plot in plots]
        }

    return JsonResponse({'success': True, 'plot_data': plot_data})



@login_required
@csrf_exempt
def get_plot_data(request, treatment_id):
    try:
        plots = Plot.objects.filter(Treatment_ID=treatment_id)
        plot_data = {plot.Replication_ID: {'plot_id': plot.Plot_ID, 'yield': plot.Yield, 'units': plot.Units} for plot in plots}
        print(f"Retrieved plot data for treatment {treatment_id}: {plot_data}")  # Debugging
        return JsonResponse({'success': True, 'plot_data': plot_data})
    except Exception as e:
        logger.error(f"Error fetching plot data: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@csrf_exempt
def save_plot_data(request, treatment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plot_data = data.get('plot_data', [])

            with transaction.atomic():
                # Delete existing plot data for this treatment
                Plot.objects.filter(Treatment_ID=treatment_id).delete()

                # Insert new plot data
                for plot in plot_data:
                    Plot.objects.create(
                        Treatment_ID=Treatment.objects.get(Treatment_ID=treatment_id),
                        Replication_ID=plot['replication_id'],
                        Plot_ID=plot['plot_id'],
                        Yield=plot['yield'],  # Assuming the yield data is passed in the plot_data
                        Units=plot['units']   # Assuming the units data is passed in the plot_data
                    )

            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error saving plot data: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
@csrf_exempt
def save_consolidated_plots(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plot_data = data.get('plot_data', [])

            with transaction.atomic():
                for plot in plot_data:
                    treatment_id = plot.get('treatment_id')
                    replication_id = plot.get('replication_id')
                    plot_id = plot.get('plot_id')
                    yield_value = plot.get('yield')
                    units = plot.get('units')

                    # Ensure the Treatment ID exists
                    try:
                        treatment = Treatment.objects.get(Treatment_ID=treatment_id)
                    except Treatment.DoesNotExist:
                        error_message = f"Treatment with ID {treatment_id} does not exist."
                        logger.error(error_message)
                        return JsonResponse({'success': False, 'error': error_message})

                    # Update or create the plot
                    Plot.objects.update_or_create(
                        Treatment_ID=treatment,
                        Replication_ID=int(replication_id),
                        defaults={'Plot_ID': plot_id, 'Yield': yield_value, 'Units': units}
                    )

            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error saving consolidated plots: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
@csrf_exempt
def upload_treatment_csv(request, experiment_id):
    if request.method == 'POST':
        experiment = get_object_or_404(Experiment, pk=experiment_id)
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            try:
                project_dir = os.path.join(settings.MEDIA_ROOT, 'N_trail_folder', str(experiment.Project_ID.Project_ID))
                experiment_dir = os.path.join(project_dir, str(experiment.Experiment_ID))
                treatment_dir = os.path.join(experiment_dir, 'treatments')
                os.makedirs(treatment_dir, exist_ok=True)
                
                file_path = os.path.join(treatment_dir, csv_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in csv_file.chunks():
                        destination.write(chunk)

                # Process the CSV file
                with open(file_path, 'r') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    for row in reader:
                        treatment_id = row[0]
                        replication_id = row[1]
                        plot_id = row[2]
                        yield_value = row[3]
                        units = row[4]

                        treatment, created = Treatment.objects.get_or_create(Treatment_ID=treatment_id, Experiment_ID=experiment)
                        Plot.objects.update_or_create(
                            Treatment_ID=treatment,
                            Replication_ID=replication_id,
                            defaults={'Plot_ID': plot_id, 'Yield': yield_value, 'Units': units}
                        )

                return JsonResponse({'success': True, 'file_path': file_path})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': 'No file uploaded'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
def my_projects(request):
    crop_choices = Project.CROP_CHOICES
    users = User.objects.all()  # Fetch all users to populate the project editors dropdown
    logged_in_user_email = request.user.email  # Get the logged-in user's email

    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(Project_Editors__icontains=logged_in_user_email)

    # Filter out projects without a valid Project_ID and log them
    valid_projects = []
    for project in projects:
        if project.Project_ID:
            valid_projects.append(project)
        else:
            logger.error(f"Project with missing Project_ID: {project}")

    context = {
        'projects': valid_projects,
        'crop_choices': crop_choices,
        'users': users,
    }

    return render(request, 'my_projects.html', context)



# from django.shortcuts import get_object_or_404, render
# from django.http import JsonResponse, HttpResponse
# from django.template.loader import render_to_string
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# import csv
# import os
# from itertools import product
# from django.conf import settings
# from .models import Experiment, Treatment, Plot
# from django.db import transaction
# import logging
# import json

# # Ensure logging is configured
# logger = logging.getLogger(__name__)

# @login_required
# @csrf_exempt
# def show_treatments(request, experiment_id):
#     print(f"Experiment ID: {experiment_id}")  # Debugging print statement
#     experiment = get_object_or_404(Experiment, pk=experiment_id)
    
#     treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
    
#     # Sort treatments by numeric part of Treatment_ID
#     sorted_treatments = sorted(treatments, key=lambda t: int(t.Treatment_ID.split('_T')[1]))

#     interaction_1_values = experiment.Interaction_1_value.split(',')
#     interaction_2_values = experiment.Interaction_2_value.split(',')
#     interaction_3_values = experiment.Interaction_3_value.split(',') if experiment.Interaction_3_value else ['']

#     # Collect plot data
#     plot_data = {}
#     for treatment in sorted_treatments:
#         plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
#         for plot in plots:
#             if treatment.Treatment_ID not in plot_data:
#                 plot_data[treatment.Treatment_ID] = []
#             plot_data[treatment.Treatment_ID].append({
#                 'replication_id': plot.Replication_ID,
#                 'plot_id': plot.Plot_ID,
#                 'yield': plot.Yield,
#                 'units': plot.Units
#             })

#     if request.method == 'POST':
#         if 'csv_file' in request.FILES:
#             # Handle CSV upload
#             csv_file = request.FILES['csv_file']
#             file_name = csv_file.name
#             experiment_dir = os.path.join(settings.MEDIA_ROOT, 'N_trail_folder', str(experiment_id))
#             os.makedirs(experiment_dir, exist_ok=True)
#             upload_path = os.path.join(experiment_dir, file_name)
            
#             try:
#                 with open(upload_path, 'wb+') as destination:
#                     for chunk in csv_file.chunks():
#                         destination.write(chunk)

#                 decoded_file = open(upload_path, 'r').read().splitlines()
#                 reader = csv.reader(decoded_file)

#                 with transaction.atomic():
#                     for row in reader:
#                         if row[0] != "Treatment ID":  # Skip the header
#                             treatment_id, replication_id, plot_id, yield_value, units = row
#                             Plot.objects.update_or_create(
#                                 Treatment_ID=Treatment.objects.get(Treatment_ID=treatment_id),
#                                 Replication_ID=int(replication_id),
#                                 defaults={'Plot_ID': plot_id, 'Yield': yield_value, 'Units': units}
#                             )

#                 # Save file name and path in session
#                 request.session['uploaded_file_name'] = file_name
#                 request.session['uploaded_file_path'] = f'/media/N_trail_folder/{experiment_id}/{file_name}'

#                 return JsonResponse({'success': True, 'file_name': file_name, 'file_path': request.session['uploaded_file_path']})
#             except Exception as e:
#                 logger.error(f"Error uploading plot data: {str(e)}", exc_info=True)
#                 return JsonResponse({'success': False, 'error': str(e)})

#         try:
#             data = json.loads(request.body)
#             action = data.get('action')
#             if action == 'submit_all':
#                 treatments_data = data.get('treatments', [])
#                 deleted_treatments = data.get('deleted_treatments', [])

#                 with transaction.atomic():
#                     # Delete treatments
#                     for treatment_id in deleted_treatments:
#                         Treatment.objects.filter(Treatment_ID=treatment_id).delete()

#                     # Get the max numeric part of the Treatment_ID within this experiment
#                     existing_ids = Treatment.objects.filter(Experiment_ID=experiment).values_list('Treatment_ID', flat=True)
#                     max_numeric_id = 0
#                     for id in existing_ids:
#                         numeric_part = id.split('_T')[1]
#                         if numeric_part.isdigit():
#                             numeric_part = int(numeric_part)
#                             if numeric_part > max_numeric_id:
#                                 max_numeric_id = numeric_part

#                     # Update or create treatments
#                     for treatment in treatments_data:
#                         treatment_id = treatment.get('treatment_id')
#                         interaction_1_value = treatment.get('interaction_1_value', '').strip()
#                         interaction_2_value = treatment.get('interaction_2_value', '').strip()
#                         interaction_3_value = treatment.get('interaction_3_value', '').strip()
#                         no_of_replication = treatment.get('no_of_replication', '').strip()
#                         metadata = treatment.get('metadata', '').strip()

#                         # Ensure at least one interaction value is provided
#                         if not interaction_1_value and not interaction_2_value and not interaction_3_value:
#                             raise ValueError(f"At least one interaction value must be provided for treatment {treatment_id}")

#                         # Ensure no_of_replication is provided
#                         if not no_of_replication:
#                             raise ValueError(f"No_of_Replication for treatment {treatment_id} cannot be empty")

#                         # Generate new Treatment_ID if it's a new treatment
#                         if not treatment_id.startswith(f"{experiment_id}_T"):
#                             max_numeric_id += 1
#                             treatment_id = f"{experiment_id}_T{max_numeric_id}"

#                         # Update or create the treatment
#                         Treatment.objects.update_or_create(
#                             Treatment_ID=treatment_id,
#                             Experiment_ID=experiment,
#                             defaults={
#                                 'Interaction_1_Value': interaction_1_value,
#                                 'Interaction_2_Value': interaction_2_value,
#                                 'Interaction_3_Value': interaction_3_value,
#                                 'No_of_Replication': no_of_replication,
#                                 'MetaData': metadata
#                             }
#                         )

#                 # Re-fetch and sort treatments after updates
#                 treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
#                 sorted_treatments = sorted(treatments, key=lambda t: int(t.Treatment_ID.split('_T')[1]))

#                 return JsonResponse({'success': True})
#         except Exception as e:
#             logger.error(f"Error submitting treatments: {str(e)}", exc_info=True)
#             return JsonResponse({'success': False, 'error': str(e)})

#     if request.method == 'GET' and 'download' in request.GET:
#         units = request.GET.get('units', 'u1')
#         print(f"Downloading CSV with units: {units}")  # Debugging print statement
#         # Handle CSV download
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = f'attachment; filename="plot_table_{experiment_id}.csv"'

#         writer = csv.writer(response)
#         writer.writerow(['Treatment ID', 'Replication ID', 'Plot ID', 'Yield', 'Units'])

#         for treatment in sorted_treatments:
#             for rep in range(1, int(treatment.No_of_Replication) + 1):
#                 writer.writerow([str(treatment.Treatment_ID), str(rep), '', '', units])

#         return response

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': sorted_treatments, 'units': 'u1'}, request)
#         return JsonResponse({'html': html})

#     no_of_replicates = request.GET.get('no_of_replicates', '1')

#     combinations = list(product(interaction_1_values, interaction_2_values, interaction_3_values))
#     num_combinations = len(combinations)

#     if not treatments.exists():
#         existing_ids = Treatment.objects.values_list('Treatment_ID', flat=True)
#         new_treatment_id = max([int(id.split('_T')[1]) for id in existing_ids if id.split('_T')[1].isdigit()]) + 1 if existing_ids else 1

#         for combination in combinations:
#             while f"{experiment_id}_T{new_treatment_id}" in existing_ids:
#                 new_treatment_id += 1
#             Treatment.objects.create(
#                 Treatment_ID=f"{experiment_id}_T{new_treatment_id}",
#                 Experiment_ID=experiment,
#                 Interaction_1_Value=combination[0],
#                 Interaction_2_Value=combination[1],
#                 Interaction_3_Value=combination[2],
#                 No_of_Replication=no_of_replicates,
#                 MetaData='Generated'
#             )
#             new_treatment_id += 1
#         treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
#         # Ensure treatments are sorted after generation
#         sorted_treatments = sorted(treatments, key=lambda t: int(t.Treatment_ID.split('_T')[1]))

#     uploaded_file_name = request.session.get('uploaded_file_name')
#     uploaded_file_path = request.session.get('uploaded_file_path')

#     # Capture units from GET parameters or set default
#     units = request.GET.get('units', 'na')  # Default to 'na' if not specified
#     print(f"Units parameter passed to context: {units}")  # Debugging print statement

#     return render(request, 'show_treatments.html', {
#         'experiment': experiment,
#         'treatments': sorted_treatments,
#         'plot_data': plot_data,
#         'uploaded_file_name': uploaded_file_name,
#         'uploaded_file_path': uploaded_file_path,
#         'units': units  # Pass units to the context
#     })





@csrf_exempt
def project_database(request):
    filter_type = request.GET.get('filter_type', '')
    project_column = request.GET.get('project_column', '')
    project_value = request.GET.get('project_value', '')
    interaction_1_value = request.GET.get('interaction_1_value', '')
    interaction_2_value = request.GET.get('interaction_2_value', '')
    interaction_3_value = request.GET.get('interaction_3_value', '')
    experiment_column = request.GET.get('experiment_column', '')
    experiment_value = request.GET.get('experiment_value', '')
    interaction_values = []

    projects = Project.objects.all()
    experiments = Experiment.objects.all()

    if filter_type == 'projects':
        if project_column and project_value:
            if project_column in ['Project_ID', 'User_ID', 'Interactions_count', 'Crop', 'Project_Editors', 'Funding_Source']:
                filter_kwargs = {f'{project_column}__exact': project_value}
            else:
                filter_kwargs = {f'{project_column}__icontains': project_value}
            projects = projects.filter(**filter_kwargs)
        if interaction_1_value:
            projects = projects.filter(Interaction_1__icontains=interaction_1_value)
        if interaction_2_value:
            projects = projects.filter(Interaction_2__icontains=interaction_2_value)
        if interaction_3_value:
            projects = projects.filter(Interaction_3__icontains=interaction_3_value)
    elif filter_type == 'experiments':
        if experiment_column and experiment_value:
            if experiment_column in ['Experiment_ID', 'Project_ID', 'Location_ID', 'Year']:
                filter_kwargs = {f'{experiment_column}__exact': experiment_value}
            else:
                filter_kwargs = {f'{experiment_column}__icontains': experiment_value}
            experiments = experiments.filter(**filter_kwargs)
        if experiment_column == 'Interaction':
            interaction_values = [
                request.GET.get('Interaction_1_value', ''),
                request.GET.get('Interaction_2_value', ''),
                request.GET.get('Interaction_3_value', '')
            ]
            if interaction_values[0]:
                experiments = experiments.filter(Interaction_1_value__icontains=interaction_values[0])
            if interaction_values[1]:
                experiments = experiments.filter(Interaction_2_value__icontains=interaction_values[1])
            if interaction_values[2]:
                experiments = experiments.filter(Interaction_3_value__icontains=interaction_values[2])

    return render(request, 'project_database.html', {
        'projects': projects,
        'experiments': experiments,
        'filter_type': filter_type
    })

def get_column_values(request):
    column = request.GET.get('column', '')
    filter_type = request.GET.get('type', '')
    values = []

    if filter_type == 'project' and column:
        values = Project.objects.values_list(column, flat=True).distinct()
    elif filter_type == 'experiment' and column:
        values = Experiment.objects.values_list(column, flat=True).distinct()

    return JsonResponse({'values': list(values)})



@login_required
@csrf_exempt
def show_treatments(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
    
    sorted_treatments = sorted(treatments, key=lambda t: int(t.Treatment_ID.split('_T')[1]))

    interaction_1_values = experiment.Interaction_1_value.split(',')
    interaction_2_values = experiment.Interaction_2_value.split(',')
    interaction_3_values = experiment.Interaction_3_value.split(',') if experiment.Interaction_3_value else ['']

    plot_data = {}
    for treatment in sorted_treatments:
        plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
        for plot in plots:
            if treatment.Treatment_ID not in plot_data:
                plot_data[treatment.Treatment_ID] = []
            plot_data[treatment.Treatment_ID].append({
                'replication_id': plot.Replication_ID,
                'plot_id': plot.Plot_ID,
                'yield': plot.Yield,
                'units': plot.Units
            })

    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            file_name = csv_file.name
            experiment_dir = os.path.join(settings.MEDIA_ROOT, 'N_trail_folder', str(experiment_id))
            os.makedirs(experiment_dir, exist_ok=True)
            upload_path = os.path.join(experiment_dir, file_name)
            
            try:
                with open(upload_path, 'wb+') as destination:
                    for chunk in csv_file.chunks():
                        destination.write(chunk)

                decoded_file = open(upload_path, 'r').read().splitlines()
                reader = csv.reader(decoded_file)

                with transaction.atomic():
                    for row in reader:
                        if row[0] != "Treatment ID":
                            treatment_id, replication_id, plot_id, yield_value, units = row
                            Plot.objects.update_or_create(
                                Treatment_ID=Treatment.objects.get(Treatment_ID=treatment_id),
                                Replication_ID=int(replication_id),
                                defaults={'Plot_ID': plot_id, 'Yield': yield_value, 'Units': units}
                            )

                request.session['uploaded_file_name'] = file_name
                request.session['uploaded_file_path'] = f'/media/N_trail_folder/{experiment_id}/{file_name}'

                return JsonResponse({'success': True, 'file_name': file_name, 'file_path': request.session['uploaded_file_path']})
            except Exception as e:
                logger.error(f"Error uploading plot data: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'error': str(e)})

        try:
            data = json.loads(request.body)
            action = data.get('action')
            if action == 'submit_all':
                treatments_data = data.get('treatments', [])
                deleted_treatments = data.get('deleted_treatments', [])

                with transaction.atomic():
                    for treatment_id in deleted_treatments:
                        Treatment.objects.filter(Treatment_ID=treatment_id).delete()

                    existing_ids = Treatment.objects.filter(Experiment_ID=experiment).values_list('Treatment_ID', flat=True)
                    max_numeric_id = 0
                    for id in existing_ids:
                        numeric_part = id.split('_T')[1]
                        if numeric_part.isdigit():
                            numeric_part = int(numeric_part)
                            if numeric_part > max_numeric_id:
                                max_numeric_id = numeric_part

                    for treatment in treatments_data:
                        treatment_id = treatment.get('treatment_id')
                        interaction_1_value = treatment.get('interaction_1_value', '').strip()
                        interaction_2_value = treatment.get('interaction_2_value', '').strip()
                        interaction_3_value = treatment.get('interaction_3_value', '').strip()
                        no_of_replication = treatment.get('no_of_replication', '').strip()
                        metadata = treatment.get('metadata', '').strip()

                        if not interaction_1_value and not interaction_2_value and not interaction_3_value:
                            raise ValueError(f"At least one interaction value must be provided for treatment {treatment_id}")

                        if not no_of_replication:
                            raise ValueError(f"No_of_Replication for treatment {treatment_id} cannot be empty")

                        if not treatment_id.startswith(f"{experiment_id}_T"):
                            max_numeric_id += 1
                            treatment_id = f"{experiment_id}_T{max_numeric_id}"

                        Treatment.objects.update_or_create(
                            Treatment_ID=treatment_id,
                            Experiment_ID=experiment,
                            defaults={
                                'Interaction_1_Value': interaction_1_value,
                                'Interaction_2_Value': interaction_2_value,
                                'Interaction_3_Value': interaction_3_value,
                                'No_of_Replication': no_of_replication,
                                'MetaData': metadata
                            }
                        )

                treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
                sorted_treatments = sorted(treatments, key=lambda t: int(t.Treatment_ID.split('_T')[1]))

                return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error submitting treatments: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    if request.method == 'GET' and 'download' in request.GET:
        units = request.GET.get('units', 'u1')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="plot_table_{experiment_id}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Treatment ID', 'Replication ID', 'Plot ID', 'Yield', 'Units'])

        for treatment in sorted_treatments:
            for rep in range(1, int(treatment.No_of_Replication) + 1):
                writer.writerow([str(treatment.Treatment_ID), str(rep), '', '', units])

        return response

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': sorted_treatments, 'units': 'u1'}, request)
        return JsonResponse({'html': html})

    if request.method == 'GET' and 'generate_graph' in request.GET:
        graph_type = request.GET.get('graph_type', 'individual')
        if graph_type == 'average':
            return generate_average_yield_graph(sorted_treatments)
        else:
            return generate_individual_yield_graph(sorted_treatments)

    uploaded_file_name = request.session.get('uploaded_file_name')
    uploaded_file_path = request.session.get('uploaded_file_path')

    units = request.GET.get('units', 'na')

    return render(request, 'show_treatments.html', {
        'experiment': experiment,
        'treatments': sorted_treatments,
        'plot_data': plot_data,
        'uploaded_file_name': uploaded_file_name,
        'uploaded_file_path': uploaded_file_path,
        'units': units,
        'interaction_1_values': interaction_1_values,
        'interaction_2_values': interaction_2_values,
        'interaction_3_values': interaction_3_values
    })



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import io
import base64
from .models import Treatment, Plot

def generate_individual_yield_graph(request, experiment_id):
    if request.method == 'GET':
        try:
            treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
            treatment_ids = []
            yields = []
            colors = []
            color_map = {}

            pastel_colors = [
                '#AEC6CF', '#FFB347', '#B39EB5', '#77DD77', '#FF6961',
                '#FDFD96', '#CFCFC4', '#B19CD9', '#FFD1DC', '#B0E0E6'
            ]

            for i, treatment in enumerate(treatments):
                plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
                for plot in plots:
                    treatment_ids.append(f"{treatment.Treatment_ID}_{plot.Replication_ID}")
                    yields.append(plot.Yield)
                    if treatment.Treatment_ID not in color_map:
                        color_map[treatment.Treatment_ID] = pastel_colors[i % len(pastel_colors)]
                    colors.append(color_map[treatment.Treatment_ID])
            
            plt.figure(figsize=(10, 8))
            bars = plt.bar(treatment_ids, yields, color=colors, width=0.5)
            plt.xlabel('Treatment ID')
            plt.ylabel('Yield')
            plt.title('Individual Yield Values')
            plt.xticks(rotation=90)

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            image_png = buf.getvalue()
            buf.close()
            graph = base64.b64encode(image_png).decode('utf-8')
            return JsonResponse({'graph': graph})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            interaction1 = data.get('interaction1', '')
            interaction2 = data.get('interaction2', '')
            interaction3 = data.get('interaction3', '')
            treatment_filter = data.get('treatmentFilter', '')

            treatments = Treatment.objects.filter(
                Experiment_ID=experiment_id,
                Interaction_1_Value__icontains=interaction1,
                Interaction_2_Value__icontains=interaction2,
                Interaction_3_Value__icontains=interaction3
            )
            
            if treatment_filter:
                treatments = treatments.filter(Treatment_ID=treatment_filter)

            treatment_ids = []
            yields = []
            colors = []
            color_map = {}

            pastel_colors = [
                '#AEC6CF', '#FFB347', '#B39EB5', '#77DD77', '#FF6961',
                '#FDFD96', '#CFCFC4', '#B19CD9', '#FFD1DC', '#B0E0E6'
            ]

            for i, treatment in enumerate(treatments):
                plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
                for plot in plots:
                    treatment_ids.append(f"{treatment.Treatment_ID}_{plot.Replication_ID}")
                    yields.append(plot.Yield)
                    if treatment.Treatment_ID not in color_map:
                        color_map[treatment.Treatment_ID] = pastel_colors[i % len(pastel_colors)]
                    colors.append(color_map[treatment.Treatment_ID])
            
            plt.figure(figsize=(10, 8))
            bars = plt.bar(treatment_ids, yields, color=colors, width=0.5)
            plt.xlabel('Treatment ID')
            plt.ylabel('Yield')
            plt.title('Individual Yield Values')
            plt.xticks(rotation=90)

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            image_png = buf.getvalue()
            buf.close()
            graph = base64.b64encode(image_png).decode('utf-8')
            return JsonResponse({'graph': graph})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})

def generate_average_yield_graph(request, experiment_id):
    if request.method == 'GET':
        try:
            treatments = Treatment.objects.filter(Experiment_ID=experiment_id)
            treatment_ids = []
            avg_yields = []
            colors = []
            color_map = {}

            pastel_colors = [
                '#AEC6CF', '#FFB347', '#B39EB5', '#77DD77', '#FF6961',
                '#FDFD96', '#CFCFC4', '#B19CD9', '#FFD1DC', '#B0E0E6'
            ]

            for i, treatment in enumerate(treatments):
                plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
                if plots.exists():
                    avg_yield = sum([plot.Yield for plot in plots]) / len(plots)
                else:
                    avg_yield = 0
                treatment_ids.append(treatment.Treatment_ID)
                avg_yields.append(avg_yield)
                if treatment.Treatment_ID not in color_map:
                    color_map[treatment.Treatment_ID] = pastel_colors[i % len(pastel_colors)]
                colors.append(color_map[treatment.Treatment_ID])
            
            plt.figure(figsize=(6, 6))
            bars = plt.bar(treatment_ids, avg_yields, color=colors, width=0.3)
            plt.xlabel('Treatment ID')
            plt.ylabel('Average Yield')
            plt.title('Average Yield Values')
            plt.xticks(rotation=90)

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            image_png = buf.getvalue()
            buf.close()
            graph = base64.b64encode(image_png).decode('utf-8')
            return JsonResponse({'graph': graph})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            interaction1 = data.get('interaction1', '')
            interaction2 = data.get('interaction2', '')
            interaction3 = data.get('interaction3', '')
            treatment_filter = data.get('treatmentFilter', '')

            treatments = Treatment.objects.filter(
                Experiment_ID=experiment_id,
                Interaction_1_Value__icontains=interaction1,
                Interaction_2_Value__icontains=interaction2,
                Interaction_3_Value__icontains=interaction3
            )
            
            if treatment_filter:
                treatments = treatments.filter(Treatment_ID=treatment_filter)

            treatment_ids = []
            avg_yields = []
            colors = []
            color_map = {}

            pastel_colors = [
                '#AEC6CF', '#FFB347', '#B39EB5', '#77DD77', '#FF6961',
                '#FDFD96', '#CFCFC4', '#B19CD9', '#FFD1DC', '#B0E0E6'
            ]

            for i, treatment in enumerate(treatments):
                plots = Plot.objects.filter(Treatment_ID=treatment.Treatment_ID)
                if plots.exists():
                    avg_yield = sum([plot.Yield for plot in plots]) / len(plots)
                else:
                    avg_yield = 0
                treatment_ids.append(treatment.Treatment_ID)
                avg_yields.append(avg_yield)
                if treatment.Treatment_ID not in color_map:
                    color_map[treatment.Treatment_ID] = pastel_colors[i % len(pastel_colors)]
                colors.append(color_map[treatment.Treatment_ID])
            
            plt.figure(figsize=(6, 6))
            bars = plt.bar(treatment_ids, avg_yields, color=colors, width=0.3)
            plt.xlabel('Treatment ID')
            plt.ylabel('Average Yield')
            plt.title('Average Yield Values')
            plt.xticks(rotation=90)

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            image_png = buf.getvalue()
            buf.close()
            graph = base64.b64encode(image_png).decode('utf-8')
            return JsonResponse({'graph': graph})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})

