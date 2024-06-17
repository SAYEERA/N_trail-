from django.shortcuts import render,get_object_or_404,redirect
from .models import Project, Location, Experiment, Treatment, Plot
from django.http import JsonResponse
from itertools import product
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import random
import json
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

def home(request):
    return render(request, 'home.html')

def browse(request):
    return render(request, 'browse.html')


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

def show_experiments(request, project_id):
    location_choices = Experiment.LOCATION_CHOICES
    project = get_object_or_404(Project, pk=project_id)
    experiments = Experiment.objects.filter(Project_ID=project)


    context ={'experiments': experiments, 
              'location_choices': location_choices,
              'project': project,
            
     }
    return render(request, 'show_experiments.html',context )


def all_projects(request):
    return render(request, 'all_projects.html')

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


# def project_database(request):
#     return render(request, 'project_database.html')
@csrf_exempt
def project_database(request):
    projects = Project.objects.all()  # Fetch all project data
    return render(request, 'project_database.html', {'projects': projects})


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



# @login_required
# def show_treatments(request, experiment_id):
#     experiment = get_object_or_404(Experiment, pk=experiment_id)
#     treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     interaction_1_values = experiment.Interaction_1_value.split(',')
#     interaction_2_values = experiment.Interaction_2_value.split(',')
#     interaction_3_values = experiment.Interaction_3_value.split(',') if experiment.Interaction_3_value else ['']

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': treatments}, request)
#         return JsonResponse({'html': html})

#     combinations = list(product(interaction_1_values, interaction_2_values, interaction_3_values))
#     num_combinations = len(combinations)

#     if not treatments.exists():
#         existing_ids = set(Treatment.objects.values_list('Treatment_ID', flat=True))
#         new_treatment_id = max(existing_ids) + 1 if existing_ids else 1

#         for combination in combinations:
#             while new_treatment_id in existing_ids:
#                 new_treatment_id += 1
#             Treatment.objects.create(
#                 Treatment_ID=new_treatment_id,
#                 Experiment_ID=experiment,
#                 Interaction_1_Value=combination[0],
#                 Interaction_2_Value=combination[1],
#                 Interaction_3_Value=combination[2],
#                 No_of_Replication='1',
#                 MetaData='Generated'
#             )
#             new_treatment_id += 1
#         treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})



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

# @csrf_exempt
# @login_required
# def add_experiment(request):
#     if request.method == 'POST':
#         try:
#             project_id = request.POST.get('Project_ID')
#             experiment_id = request.POST.get('Experiment_ID')
#             year = request.POST.get('Year')
#             location_id = request.POST.get('Location_ID')
#             interaction_1_count = request.POST.get('Interaction_1_count', '0') or '0'
#             interaction_2_count = request.POST.get('Interaction_2_count', '0') or '0'
#             interaction_3_count = request.POST.get('Interaction_3_count', '0') or '0'
#             metadata = request.POST.get('MetaData')

#             # Convert interaction counts to integers
#             interaction_1_count = int(interaction_1_count)
#             interaction_2_count = int(interaction_2_count)
#             interaction_3_count = int(interaction_3_count)

#             # Fetch the Project instance
#             project = get_object_or_404(Project, pk=project_id)

#             # Handle the "Other" location option
#             if location_id == 'other':
#                 location_data = {
#                     'Location_ID': request.POST.get('New_Location_ID'),
#                     'State': request.POST.get('New_State'),
#                     'County': request.POST.get('New_County'),
#                     'Owner': request.POST.get('New_Owner'),
#                     'Latitude': request.POST.get('New_Latitude'),
#                     'Longitude': request.POST.get('New_Longitude'),
#                     'Contact': request.POST.get('New_Contact'),
#                     'MetaData': request.POST.get('New_MetaData')
#                 }
#                 location = Location.objects.create(**location_data)
#                 location_id = location.Location_ID
#             else:
#                 location = get_object_or_404(Location, pk=location_id)

#             # Save the experiment data to the database
#             experiment = Experiment.objects.create(
#                 Experiment_ID=experiment_id,
#                 Project_ID=project,
#                 Location_ID=location,
#                 Year=year,
#                 Interaction_1_count=interaction_1_count,
#                 Interaction_2_count=interaction_2_count,
#                 Interaction_3_count=interaction_3_count,
#                 MetaData=metadata
#             )

#             # Save dynamically generated fields
#             interaction_1_values = []
#             interaction_2_values = []
#             interaction_3_values = []

#             for i in range(1, interaction_1_count + 1):
#                 value = request.POST.get(f'Interaction_1_{i}', 'NA')
#                 interaction_1_values.append(value)

#             for i in range(1, interaction_2_count + 1):
#                 value = request.POST.get(f'Interaction_2_{i}', 'NA')
#                 interaction_2_values.append(value)

#             for i in range(1, interaction_3_count + 1):
#                 value = request.POST.get(f'Interaction_3_{i}', 'NA')
#                 interaction_3_values.append(value)

#             experiment.Interaction_1_value = ','.join(interaction_1_values)
#             experiment.Interaction_2_value = ','.join(interaction_2_values)
#             experiment.Interaction_3_value = ','.join(interaction_3_values)

#             # Save additional fields
#             experiment.Yield_Map = request.POST.get('Yield_Map', '')
#             experiment.Soil_Sample = request.POST.get('Soil_Sample', '')
#             experiment.Sonic_sensor = request.POST.get('Sonic_sensor', '')
#             experiment.GCP = request.POST.get('GCP', '')
#             experiment.RAWUAV = request.POST.get('RAWUAV', '')
#             experiment.Orthomosic_UAV = request.POST.get('Orthomosic_UAV', '')
#             experiment.DSM_UAV = request.POST.get('DSM_UAV', '')
#             experiment.Orthomosic_SAT = request.POST.get('Orthomosic_SAT', '')
#             experiment.DSM_SAT = request.POST.get('DSM_SAT', '')
#             experiment.VI_1 = request.POST.get('VI_1', '')
#             experiment.VI_2 = request.POST.get('VI_2', '')
#             experiment.VI_3 = request.POST.get('VI_3', '')

#             experiment.save()

#             # Redirect to show_treatments after saving experiment
#             return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})



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
            start_year = request.POST.get('Start_year')
            interactions_count = request.POST.get('Interactions_count')
            interaction_1 = request.POST.get('Interaction_1')
            interaction_2 = request.POST.get('Interaction_2')
            interaction_3 = request.POST.get('Interaction_3')
            crop = request.POST.get('Crop')
            no_of_years = request.POST.get('No_of_Year')
            project_editors = request.POST.get('Project_Editors')
            funding_source = request.POST.get('Funding_Source')
            metadata = request.POST.get('MetaData')
            view_type = request.POST.get('View_Type')

            # Create the project
            project = Project.objects.create(
                Project_ID=project_id,
                User_ID_id=user_id,
                Start_year=start_year,
                Interactions_count=interactions_count,
                Interaction_1=interaction_1,
                Interaction_2=interaction_2,
                Interaction_3=interaction_3,
                Crop=crop,
                No_of_Year=no_of_years,
                Project_Editors=project_editors,
                Funding_Source=funding_source,
                MetaData=metadata,
                View_Type=view_type
            )

            # Create folder and save project details as a .txt file
            # base_dir = os.path.join(settings.BASE_DIR, 'N_trail_folder')
            base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')


            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            project_dir = os.path.join(base_dir, project_id)
            os.makedirs(project_dir, exist_ok=True)

            print(f"Base directory: {base_dir}")
            print(f"Project directory: {project_dir}")

            file_path = os.path.join(project_dir, f'{project_id}.txt')
            with open(file_path, 'w') as file:
                file.write(f'Project ID: {project_id}\n')
                file.write(f'User ID: {user_id}\n')
                file.write(f'Start Year: {start_year}\n')
                file.write(f'Interactions Count: {interactions_count}\n')
                file.write(f'Interaction 1: {interaction_1}\n')
                file.write(f'Interaction 2: {interaction_2}\n')
                file.write(f'Interaction 3: {interaction_3}\n')
                file.write(f'Crop: {crop}\n')
                file.write(f'Number of Years: {no_of_years}\n')
                file.write(f'Project Editors: {project_editors}\n')
                file.write(f'Funding Source: {funding_source}\n')
                file.write(f'Metadata: {metadata}\n')
                file.write(f'View Type: {view_type}\n')

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
# @login_required
# def add_experiment(request):
#     if request.method == 'POST':
#         try:
#             project_id = request.POST.get('Project_ID')
#             experiment_id = request.POST.get('Experiment_ID')
#             year = request.POST.get('Year')
#             location_id = request.POST.get('Location_ID')
#             interaction_1_count = request.POST.get('Interaction_1_count', '0') or '0'
#             interaction_2_count = request.POST.get('Interaction_2_count', '0') or '0'
#             interaction_3_count = request.POST.get('Interaction_3_count', '0') or '0'
#             metadata = request.POST.get('MetaData')
#             no_of_replicates = request.POST.get('No_of_Replicates')

#             # Convert interaction counts to integers
#             interaction_1_count = int(interaction_1_count)
#             interaction_2_count = int(interaction_2_count)
#             interaction_3_count = int(interaction_3_count)

#             # Fetch the Project instance
#             project = get_object_or_404(Project, pk=project_id)

#             # Handle the "Other" location option
#             if location_id == 'other':
#                 location_data = {
#                     'Location_ID': request.POST.get('New_Location_ID'),
#                     'State': request.POST.get('New_State'),
#                     'County': request.POST.get('New_County'),
#                     'Owner': request.POST.get('New_Owner'),
#                     'Latitude': request.POST.get('New_Latitude'),
#                     'Longitude': request.POST.get('New_Longitude'),
#                     'Contact': request.POST.get('New_Contact'),
#                     'MetaData': request.POST.get('New_MetaData')
#                 }
#                 location = Location.objects.create(**location_data)
#                 location_id = location.Location_ID
#             else:
#                 location = get_object_or_404(Location, pk=location_id)

#             # Save the experiment data to the database
#             experiment = Experiment.objects.create(
#                 Experiment_ID=experiment_id,
#                 Project_ID=project,
#                 Location_ID=location,
#                 Year=year,
#                 Interaction_1_count=interaction_1_count,
#                 Interaction_2_count=interaction_2_count,
#                 Interaction_3_count=interaction_3_count,
#                 MetaData=metadata
#             )

#             # Save dynamically generated fields
#             interaction_1_values = []
#             interaction_2_values = []
#             interaction_3_values = []

#             for i in range(1, interaction_1_count + 1):
#                 value = request.POST.get(f'Interaction_1_{i}', 'NA')
#                 interaction_1_values.append(value)

#             for i in range(1, interaction_2_count + 1):
#                 value = request.POST.get(f'Interaction_2_{i}', 'NA')
#                 interaction_2_values.append(value)

#             for i in range(1, interaction_3_count + 1):
#                 value = request.POST.get(f'Interaction_3_{i}', 'NA')
#                 interaction_3_values.append(value)

#             experiment.Interaction_1_value = ','.join(interaction_1_values)
#             experiment.Interaction_2_value = ','.join(interaction_2_values)
#             experiment.Interaction_3_value = ','.join(interaction_3_values)

#             # Save additional fields
#             experiment.Yield_Map = request.POST.get('Yield_Map', '')
#             experiment.Soil_Sample = request.POST.get('Soil_Sample', '')
#             experiment.Sonic_sensor = request.POST.get('Sonic_sensor', '')
#             experiment.GCP = request.POST.get('GCP', '')
#             experiment.RAWUAV = request.POST.get('RAWUAV', '')
#             experiment.Orthomosic_UAV = request.POST.get('Orthomosic_UAV', '')
#             experiment.DSM_UAV = request.POST.get('DSM_UAV', '')
#             experiment.Orthomosic_SAT = request.POST.get('Orthomosic_SAT', '')
#             experiment.DSM_SAT = request.POST.get('DSM_SAT', '')
#             experiment.VI_1 = request.POST.get('VI_1', '')
#             experiment.VI_2 = request.POST.get('VI_2', '')
#             experiment.VI_3 = request.POST.get('VI_3', '')

#             experiment.save()

#             # Redirect to show_treatments after saving experiment
#             return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID, 'no_of_replicates': no_of_replicates})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @login_required
# @csrf_exempt
# def show_treatments(request, experiment_id):
#     experiment = get_object_or_404(Experiment, pk=experiment_id)
#     treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     interaction_1_values = experiment.Interaction_1_value.split(',')
#     interaction_2_values = experiment.Interaction_2_value.split(',')
#     interaction_3_values = experiment.Interaction_3_value.split(',') if experiment.Interaction_3_value else ['']

#     if request.method == 'POST':
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

#                 return JsonResponse({'success': True})
#         except Exception as e:
#             logger.error(f"Error submitting treatments: {str(e)}", exc_info=True)
#             return JsonResponse({'success': False, 'error': str(e)})

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': treatments}, request)
#         return JsonResponse({'html': html})

#     no_of_replicates = request.GET.get('no_of_replicates', '1')

#     combinations = list(product(interaction_1_values, interaction_2_values, interaction_3_values))
#     num_combinations = len(combinations)

#     if not treatments.exists():
#         existing_ids = set(Treatment.objects.values_list('Treatment_ID', flat=True))
#         new_treatment_id = max(existing_ids) + 1 if existing_ids else 1

#         for combination in combinations:
#             while new_treatment_id in existing_ids:
#                 new_treatment_id += 1
#             Treatment.objects.create(
#                 Treatment_ID=new_treatment_id,
#                 Experiment_ID=experiment,
#                 Interaction_1_Value=combination[0],
#                 Interaction_2_Value=combination[1],
#                 Interaction_3_Value=combination[2],
#                 No_of_Replication=no_of_replicates,
#                 MetaData='Generated'
#             )
#             new_treatment_id += 1
#         treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})



# @login_required
# def add_experiment(request):
#     if request.method == 'POST':
#         try:
#             project_id = request.POST.get('Project_ID')
#             experiment_id = request.POST.get('Experiment_ID')
#             year = request.POST.get('Year')
#             location_id = request.POST.get('Location_ID')
#             interaction_1_count = request.POST.get('Interaction_1_count', '0') or '0'
#             interaction_2_count = request.POST.get('Interaction_2_count', '0') or '0'
#             interaction_3_count = request.POST.get('Interaction_3_count', '0') or '0'
#             metadata = request.POST.get('MetaData')
#             no_of_replicates = request.POST.get('No_of_Replicates')

#             # Convert interaction counts to integers
#             interaction_1_count = int(interaction_1_count)
#             interaction_2_count = int(interaction_2_count)
#             interaction_3_count = int(interaction_3_count)

#             # Fetch the Project instance
#             project = get_object_or_404(Project, pk=project_id)

#             # Handle the "Other" location option
#             if location_id == 'other':
#                 location_data = {
#                     'Location_ID': request.POST.get('New_Location_ID'),
#                     'State': request.POST.get('New_State'),
#                     'County': request.POST.get('New_County'),
#                     'Owner': request.POST.get('New_Owner'),
#                     'Latitude': request.POST.get('New_Latitude'),
#                     'Longitude': request.POST.get('New_Longitude'),
#                     'Contact': request.POST.get('New_Contact'),
#                     'MetaData': request.POST.get('New_MetaData')
#                 }
#                 location = Location.objects.create(**location_data)
#                 location_id = location.Location_ID
#             else:
#                 location = get_object_or_404(Location, pk=location_id)

#             # Save the experiment data to the database
#             experiment = Experiment.objects.create(
#                 Experiment_ID=experiment_id,
#                 Project_ID=project,
#                 Location_ID=location,
#                 Year=year,
#                 Interaction_1_count=interaction_1_count,
#                 Interaction_2_count=interaction_2_count,
#                 Interaction_3_count=interaction_3_count,
#                 MetaData=metadata
#             )

#             # Save dynamically generated fields
#             interaction_1_values = []
#             interaction_2_values = []
#             interaction_3_values = []

#             for i in range(1, interaction_1_count + 1):
#                 value = request.POST.get(f'Interaction_1_{i}', 'NA')
#                 interaction_1_values.append(value)

#             for i in range(1, interaction_2_count + 1):
#                 value = request.POST.get(f'Interaction_2_{i}', 'NA')
#                 interaction_2_values.append(value)

#             for i in range(1, interaction_3_count + 1):
#                 value = request.POST.get(f'Interaction_3_{i}', 'NA')
#                 interaction_3_values.append(value)

#             experiment.Interaction_1_value = ','.join(interaction_1_values)
#             experiment.Interaction_2_value = ','.join(interaction_2_values)
#             experiment.Interaction_3_value = ','.join(interaction_3_values)

#             experiment.save()

#             # Save experiment details to a text file
#             base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')
#             project_folder = os.path.join(base_dir, project.Project_ID)
#             experiment_folder = os.path.join(project_folder, experiment_id)
#             os.makedirs(experiment_folder, exist_ok=True)

#             file_path = os.path.join(experiment_folder, f'{experiment_id}.txt')
#             with open(file_path, 'w') as file:
#                 file.write(f'Experiment ID: {experiment_id}\n')
#                 file.write(f'Project ID: {project_id}\n')
#                 file.write(f'Location ID: {location_id}\n')
#                 file.write(f'Year: {year}\n')
#                 file.write(f'Interaction 1 Count: {interaction_1_count}\n')
#                 file.write(f'Interaction 1 Value: {experiment.Interaction_1_value}\n')
#                 file.write(f'Interaction 2 Count: {interaction_2_count}\n')
#                 file.write(f'Interaction 2 Value: {experiment.Interaction_2_value}\n')
#                 file.write(f'Interaction 3 Count: {interaction_3_count}\n')
#                 file.write(f'Interaction 3 Value: {experiment.Interaction_3_value}\n')
#                 file.write(f'Metadata: {metadata}\n')

#             return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID, 'no_of_replicates': no_of_replicates})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})

# @login_required
# @csrf_exempt
# def upload_experiment_file(request, experiment_id, file_field):
#     if request.method == 'POST':
#         experiment = get_object_or_404(Experiment, pk=experiment_id)
#         file = request.FILES.get('file')
#         if file:
#             try:
#                 base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')
#                 project_folder = os.path.join(base_dir, experiment.Project_ID.Project_ID)
#                 experiment_folder = os.path.join(project_folder, experiment.Experiment_ID)
#                 os.makedirs(experiment_folder, exist_ok=True)
#                 file_path = os.path.join(experiment_folder, file.name)
                
#                 with open(file_path, 'wb+') as destination:
#                     for chunk in file.chunks():
#                         destination.write(chunk)
                
#                 # Save the file path in the database as a relative path to make the URL work correctly
#                 file_url = os.path.relpath(file_path, settings.MEDIA_ROOT)
#                 setattr(experiment, file_field, file_url)
#                 experiment.save()
#                 return JsonResponse({'success': True, 'file_name': file.name, 'file_url': settings.MEDIA_URL + file_url})
#             except Exception as e:
#                 return JsonResponse({'success': False, 'error': str(e)})
#         return JsonResponse({'success': False, 'error': 'No file uploaded'})
#     return JsonResponse({'success': False, 'error': 'Invalid request method'})






# @login_required
# @csrf_exempt
# def show_treatments(request, experiment_id):
#     experiment = get_object_or_404(Experiment, pk=experiment_id)
#     treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     interaction_1_values = experiment.Interaction_1_value.split(',')
#     interaction_2_values = experiment.Interaction_2_value.split(',')
#     interaction_3_values = experiment.Interaction_3_value.split(',') if experiment.Interaction_3_value else ['']

#     if request.method == 'POST':
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

#                 return JsonResponse({'success': True})
#             elif action == 'save_plot_data':
#                 plot_data = data.get('plot_data', [])

#                 # Save the plot data here
#                 for plot in plot_data:
#                     treatment_id = plot.get('treatment_id')
#                     replication_id = plot.get('replication_id')
#                     plot_id = plot.get('plot_id')

#                     # Save the plot data to the database (implement your model and saving logic here)
#                     Plot.objects.update_or_create(
#                         Treatment_ID=treatment_id,
#                         Replication_ID=replication_id,
#                         defaults={
#                             'Plot_ID': plot_id,
#                         }
#                     )

#                 return JsonResponse({'success': True})
#         except Exception as e:
#             logger.error(f"Error processing request: {str(e)}", exc_info=True)
#             return JsonResponse({'success': False, 'error': str(e)})

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': treatments}, request)
#         return JsonResponse({'html': html})

#     no_of_replicates = request.GET.get('no_of_replicates', '1')

#     combinations = list(product(interaction_1_values, interaction_2_values, interaction_3_values))
#     num_combinations = len(combinations)

#     if not treatments.exists():
#         existing_ids = set(Treatment.objects.values_list('Treatment_ID', flat=True))
#         new_treatment_id = max(existing_ids) + 1 if existing_ids else 1

#         for combination in combinations:
#             while new_treatment_id in existing_ids:
#                 new_treatment_id += 1
#             Treatment.objects.create(
#                 Treatment_ID=new_treatment_id,
#                 Experiment_ID=experiment,
#                 Interaction_1_Value=combination[0],
#                 Interaction_2_Value=combination[1],
#                 Interaction_3_Value=combination[2],
#                 No_of_Replication=no_of_replicates,
#                 MetaData='Generated'
#             )
#             new_treatment_id += 1
#         treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})






@login_required
@csrf_exempt
def save_plot_data(request, treatment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plot_data = data.get('plot_data', [])

            # Ensure the treatment exists
            treatment = get_object_or_404(Treatment, Treatment_ID=treatment_id)

            # Save the plot data
            for plot in plot_data:
                replication_id = plot.get('replication_id')
                plot_id = plot.get('plot_id')

                # Save the plot data to the database
                Plot.objects.update_or_create(
                    Treatment_ID=treatment,
                    Replication_ID=replication_id,
                    defaults={'Plot_ID': plot_id}
                )

            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error saving plot data: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# @login_required
# @csrf_exempt
# def show_treatments(request, experiment_id):
#     experiment = get_object_or_404(Experiment, pk=experiment_id)
#     treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             action = data.get('action')
#             if action == 'submit_all':
#                 treatments_data = data.get('treatments', [])
#                 deleted_treatments = data.get('deleted_treatments', [])

#                 with transaction.atomic():
#                     # Delete treatments
#                     for treatment_id in deleted_treatments:
#                         Treatment.objects.filter(Treatment_ID=treatment_id, Experiment_ID=experiment).delete()

#                     # Get the max numeric part of the Treatment_ID within this experiment
#                     existing_ids = Treatment.objects.filter(Experiment_ID=experiment).values_list('Treatment_ID', flat=True)
#                     max_numeric_id = 0
#                     for id in existing_ids:
#                         numeric_part = int(id.split('e')[0])
#                         if numeric_part > max_numeric_id:
#                             max_numeric_id = numeric_part

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
#                         if treatment_id.isnumeric():
#                             max_numeric_id += 1
#                             treatment_id = f"{max_numeric_id}e{experiment.Experiment_ID}"

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

#                 return JsonResponse({'success': True})
#         except Exception as e:
#             logger.error(f"Error submitting treatments: {str(e)}", exc_info=True)
#             return JsonResponse({'success': False, 'error': str(e)})

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': treatments}, request)
#         return JsonResponse({'html': html})

#     return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})




# @login_required
# def add_experiment(request):
#     if request.method == 'POST':
#         try:
#             project_id = request.POST.get('Project_ID')
#             experiment_id = request.POST.get('Experiment_ID')
#             year = request.POST.get('Year')
#             location_id = request.POST.get('Location_ID')
#             interaction_1_count = request.POST.get('Interaction_1_count', '0') or '0'
#             interaction_2_count = request.POST.get('Interaction_2_count', '0') or '0'
#             interaction_3_count = request.POST.get('Interaction_3_count', '0') or '0'
#             metadata = request.POST.get('MetaData')
#             no_of_replicates = request.POST.get('No_of_Replicates')

#             interaction_1_count = int(interaction_1_count)
#             interaction_2_count = int(interaction_2_count)
#             interaction_3_count = int(interaction_3_count)

#             project = get_object_or_404(Project, pk=project_id)

#             if location_id == 'other':
#                 location_data = {
#                     'Location_ID': request.POST.get('New_Location_ID'),
#                     'State': request.POST.get('New_State'),
#                     'County': request.POST.get('New_County'),
#                     'Owner': request.POST.get('New_Owner'),
#                     'Latitude': request.POST.get('New_Latitude'),
#                     'Longitude': request.POST.get('New_Longitude'),
#                     'Contact': request.POST.get('New_Contact'),
#                     'MetaData': request.POST.get('New_MetaData')
#                 }
#                 location = Location.objects.create(**location_data)
#                 location_id = location.Location_ID
#             else:
#                 location = get_object_or_404(Location, pk=location_id)

#             experiment = Experiment.objects.create(
#                 Experiment_ID=experiment_id,
#                 Project_ID=project,
#                 Location_ID=location,
#                 Year=year,
#                 Interaction_1_count=interaction_1_count,
#                 Interaction_2_count=interaction_2_count,
#                 Interaction_3_count=interaction_3_count,
#                 MetaData=metadata
#             )

#             interaction_1_values = []
#             interaction_2_values = []
#             interaction_3_values = []

#             for i in range(1, interaction_1_count + 1):
#                 value = request.POST.get(f'Interaction_1_{i}', 'NA')
#                 interaction_1_values.append(value)

#             for i in range(1, interaction_2_count + 1):
#                 value = request.POST.get(f'Interaction_2_{i}', 'NA')
#                 interaction_2_values.append(value)

#             for i in range(1, interaction_3_count + 1):
#                 value = request.POST.get(f'Interaction_3_{i}', 'NA')
#                 interaction_3_values.append(value)

#             experiment.Interaction_1_value = ','.join(interaction_1_values)
#             experiment.Interaction_2_value = ','.join(interaction_2_values)
#             experiment.Interaction_3_value = ','.join(interaction_3_values)

#             experiment.save()

#             base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')
#             project_folder = os.path.join(base_dir, project.Project_ID)
#             experiment_folder = os.path.join(project_folder, experiment_id)
#             os.makedirs(experiment_folder, exist_ok=True)

#             file_path = os.path.join(experiment_folder, f'{experiment_id}.txt')
#             with open(file_path, 'w') as file:
#                 file.write(f'Experiment ID: {experiment_id}\n')
#                 file.write(f'Project ID: {project_id}\n')
#                 file.write(f'Location ID: {location_id}\n')
#                 file.write(f'Year: {year}\n')
#                 file.write(f'Interaction 1 Count: {interaction_1_count}\n')
#                 file.write(f'Interaction 1 Value: {experiment.Interaction_1_value}\n')
#                 file.write(f'Interaction 2 Count: {interaction_2_count}\n')
#                 file.write(f'Interaction 2 Value: {experiment.Interaction_2_value}\n')
#                 file.write(f'Interaction 3 Count: {interaction_3_count}\n')
#                 file.write(f'Interaction 3 Value: {experiment.Interaction_3_value}\n')
#                 file.write(f'Metadata: {metadata}\n')

#             return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID, 'no_of_replicates': no_of_replicates})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})

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
                    file_path = os.path.join(experiment_dir, file.name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    file_paths.append(os.path.relpath(file_path, settings.MEDIA_ROOT))
                
                # Update the experiment model field
                existing_files = getattr(experiment, file_field, [])
                if isinstance(existing_files, str):
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
def download_file(request, file_path):
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return HttpResponseNotFound("File not found")




# @login_required
# @csrf_exempt
# def show_treatments(request, experiment_id):
#     experiment = get_object_or_404(Experiment, pk=experiment_id)
#     treatments = Treatment.objects.filter(Experiment_ID=experiment)

#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             action = data.get('action')
#             if action == 'submit_all':
#                 treatments_data = data.get('treatments', [])
#                 deleted_treatments = data.get('deleted_treatments', [])

#                 with transaction.atomic():
#                     # Delete treatments
#                     for treatment_id in deleted_treatments:
#                         Treatment.objects.filter(Treatment_ID=treatment_id, Experiment_ID=experiment).delete()

#                     # Get the max numeric part of the Treatment_ID within this experiment
#                     existing_ids = Treatment.objects.filter(Experiment_ID=experiment).values_list('Treatment_ID', flat=True)
#                     max_numeric_id = 0
#                     for id in existing_ids:
#                         numeric_part = int(id.split('e')[0])
#                         if numeric_part > max_numeric_id:
#                             max_numeric_id = numeric_part

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

#                         # Generate new Treatment_ID if it's a new treatment
#                         if treatment_id.isnumeric():
#                             max_numeric_id += 1
#                             treatment_id = f"{max_numeric_id}e{experiment.Experiment_ID}"

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

#                 return JsonResponse({'success': True})
#         except Exception as e:
#             logger.error(f"Error submitting treatments: {str(e)}", exc_info=True)
#             return JsonResponse({'success': False, 'error': str(e)})

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': treatments}, request)
#         return JsonResponse({'html': html})

#     return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})


@login_required
def add_experiment(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('Project_ID')
            experiment_id = request.POST.get('Experiment_ID')
            year = request.POST.get('Year')
            location_id = request.POST.get('Location_ID')
            interaction_1_count = request.POST.get('Interaction_1_count', '0') or '0'
            interaction_2_count = request.POST.get('Interaction_2_count', '0') or '0'
            interaction_3_count = request.POST.get('Interaction_3_count', '0') or '0'
            metadata = request.POST.get('MetaData')
            no_of_replicates = request.POST.get('No_of_Replicates')

            interaction_1_count = int(interaction_1_count)
            interaction_2_count = int(interaction_2_count)
            interaction_3_count = int(interaction_3_count)

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

            interaction_1_values = []
            interaction_2_values = []
            interaction_3_values = []

            for i in range(1, interaction_1_count + 1):
                value = request.POST.get(f'Interaction_1_{i}', 'NA')
                interaction_1_values.append(value)

            for i in range(1, interaction_2_count + 1):
                value = request.POST.get(f'Interaction_2_{i}', 'NA')
                interaction_2_values.append(value)

            for i in range(1, interaction_3_count + 1):
                value = request.POST.get(f'Interaction_3_{i}', 'NA')
                interaction_3_values.append(value)

            experiment.Interaction_1_value = ','.join(interaction_1_values)
            experiment.Interaction_2_value = ','.join(interaction_2_values)
            experiment.Interaction_3_value = ','.join(interaction_3_values)

            experiment.save()

            base_dir = os.path.join(r'C:\Users\sayee\OneDrive\Desktop', 'N_trail_folder')
            project_folder = os.path.join(base_dir, project.Project_ID)
            experiment_folder = os.path.join(project_folder, experiment_id)
            os.makedirs(experiment_folder, exist_ok=True)

            file_path = os.path.join(experiment_folder, f'{experiment_id}.txt')
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
            interaction_combinations = list(product(
                interaction_1_values or [''],
                interaction_2_values or [''],
                interaction_3_values or ['']
            ))

            treatments = []
            treatment_id_prefix = f"{experiment_id}_T"

            for idx, (i1, i2, i3) in enumerate(interaction_combinations):
                for replicate in range(1, int(no_of_replicates) + 1):
                    treatment_id = f"{treatment_id_prefix}{idx+1}_R{replicate}"
                    treatments.append(Treatment(
                        Treatment_ID=treatment_id,
                        Experiment_ID=experiment,
                        Interaction_1_Value=i1,
                        Interaction_2_Value=i2,
                        Interaction_3_Value=i3,
                        No_of_Replication=no_of_replicates,
                        MetaData=metadata
                    ))

            Treatment.objects.bulk_create(treatments)

            return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID, 'no_of_replicates': no_of_replicates})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
@csrf_exempt
def show_treatments(request, experiment_id):
    logger.debug("Entering show_treatments view")
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    treatments = Treatment.objects.filter(Experiment_ID=experiment)
    logger.debug(f"Fetched treatments: {treatments}")

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            if action == 'submit_all':
                treatments_data = data.get('treatments', [])
                deleted_treatments = data.get('deleted_treatments', [])
                logger.debug("Processing submit_all action")

                with transaction.atomic():
                    # Delete treatments
                    for treatment_id in deleted_treatments:
                        Treatment.objects.filter(Treatment_ID=treatment_id).delete()

                    # Update or create treatments
                    for treatment in treatments_data:
                        Treatment.objects.update_or_create(
                            Treatment_ID=treatment.get('treatment_id'),
                            Experiment_ID=experiment,
                            defaults={
                                'Interaction_1_Value': treatment.get('interaction_1_value', '').strip(),
                                'Interaction_2_Value': treatment.get('interaction_2_value', '').strip(),
                                'Interaction_3_Value': treatment.get('interaction_3_value', '').strip(),
                                'No_of_Replication': treatment.get('no_of_replication', '').strip(),
                                'MetaData': treatment.get('metadata', '').strip()
                            }
                        )

                return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error submitting treatments: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})

    # Generate treatments based on the interaction counts
    interaction_1_values = experiment.Interaction_1_value.split(',')
    interaction_2_values = experiment.Interaction_2_value.split(',')
    interaction_3_values = experiment.Interaction_3_value.split(',') if experiment.Interaction_3_value else ['']
    
    combinations = list(product(interaction_1_values, interaction_2_values, interaction_3_values))
    num_combinations = len(combinations)
    
    if not treatments.exists():
        new_treatments = []
        for i, combination in enumerate(combinations, start=1):
            treatment_id = f"t{i}e{experiment_id}"
            new_treatments.append(Treatment(
                Treatment_ID=treatment_id,
                Experiment_ID=experiment,
                Interaction_1_Value=combination[0],
                Interaction_2_Value=combination[1],
                Interaction_3_Value=combination[2],
                No_of_Replication=experiment.Interaction_1_count * experiment.Interaction_2_count * experiment.Interaction_3_count,
                MetaData='Generated'
            ))
        Treatment.objects.bulk_create(new_treatments)
        treatments = Treatment.objects.filter(Experiment_ID=experiment)

    logger.debug("Rendering show_treatments template")
    return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})
