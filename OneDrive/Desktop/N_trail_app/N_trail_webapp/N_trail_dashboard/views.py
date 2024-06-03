
from django.shortcuts import render,get_object_or_404,redirect
from .models import Project, Location, Experiment, Treatment
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import random
import logging
import uuid

logger = logging.getLogger(__name__)





def home(request):
    return render(request, 'home.html')

def browse(request):
    return render(request, 'browse.html')

def my_projects(request):
    crop_choices = Project.CROP_CHOICES
    project_role_choices = Project.PROJECT_ROLE_CHOICES
    projects = Project.objects.all()
    context = {
        'projects': projects,
        'crop_choices': crop_choices,
        'project_role_choices': project_role_choices,
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

def locations(request):
    locations = Location.objects.all()
    # Render the template with the location object
    return render(request, 'locations.html', {'location': locations})


   

def data_analysis(request):
    return render(request, 'data_analysis.html')


@login_required
def add_project(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('Project_ID')
            # user_id = request.POST.get('User_ID')
            start_year = request.POST.get('Start_year')
            interactions_count = request.POST.get('Interactions_count')
            interaction_1 = request.POST.get('Interaction_1', '')
            interaction_2 = request.POST.get('Interaction_2', '')
            interaction_3 = request.POST.get('Interaction_3', '')
            crop = request.POST.get('Crop')
            no_of_years = request.POST.get('No_of_Year')
            role = request.POST.get('Role')
            funding_source = request.POST.get('Funding_Source')
            metadata = request.POST.get('MetaData')

            # Create a new Project instance
            new_project = Project(
                Project_ID=project_id,
                # User_ID=user_id,
                Start_year=start_year,
                Interactions_count=interactions_count,
                Interaction_1=interaction_1,
                Interaction_2=interaction_2,
                Interaction_3=interaction_3,
                Crop=crop,
                No_of_Year=no_of_years,
                Role=role,
                Funding_Source=funding_source,
                MetaData=metadata,
                User_ID_id=request.user.id  # Set the current user
            )
            new_project.save()
            

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
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

            # Convert interaction counts to integers
            interaction_1_count = int(interaction_1_count)
            interaction_2_count = int(interaction_2_count)
            interaction_3_count = int(interaction_3_count)

            # Fetch the Project and Location instances
            project = get_object_or_404(Project, pk=project_id)
            location = get_object_or_404(Location, pk=location_id)

            # Save the experiment data to the database
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

            # Save dynamically generated fields
            for i in range(1, interaction_1_count + 1):
                value = request.POST.get(f'Interaction_1_count_{i}', 'NA')
                setattr(experiment, f'Interaction_1_count_{i}', value)
            for i in range(1, interaction_2_count + 1):
                value = request.POST.get(f'Interaction_2_count_{i}', 'NA')
                setattr(experiment, f'Interaction_2_count_{i}', value)
            for i in range(1, interaction_3_count + 1):
                value = request.POST.get(f'Interaction_3_count_{i}', 'NA')
                setattr(experiment, f'Interaction_3_count_{i}', value)

            experiment.save()

            return JsonResponse({'success': True, 'experiment_id': experiment.Experiment_ID})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



logger = logging.getLogger(__name__)

from django.db.models import Max
import random


from django.http import JsonResponse
import random
import json

@login_required
def show_treatments(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    treatments = Treatment.objects.filter(Experiment_ID=experiment)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('show_treatments.html', {'experiment': experiment, 'treatments': treatments}, request)
        return JsonResponse({'html': html})

    interaction_1_values = [getattr(experiment, f'Interaction_1_count_{i}') for i in range(1, experiment.Interaction_1_count + 1)]
    interaction_2_values = [getattr(experiment, f'Interaction_2_count_{i}') for i in range(1, experiment.Interaction_2_count + 1)]
    interaction_3_values = [getattr(experiment, f'Interaction_3_count_{i}') for i in range(1, experiment.Interaction_3_count + 1)]

    adjusted_count_1 = max(experiment.Interaction_1_count, 1)
    adjusted_count_2 = max(experiment.Interaction_2_count, 1)
    adjusted_count_3 = max(experiment.Interaction_3_count, 1)

    num_combinations = adjusted_count_1 * adjusted_count_2 * adjusted_count_3
    logger.debug(f"Interaction combinations: {num_combinations}")

    if not treatments.exists():
        for _ in range(1, num_combinations + 1):
            existing_ids = Treatment.objects.values_list('Treatment_ID', flat=True)
            available_ids = list(set(range(1, 201)) - set(existing_ids))
            treatment_id = random.choice(available_ids)

            Treatment.objects.create(
                Treatment_ID=treatment_id,
                Experiment_ID=experiment,
                Interaction_1_Value=random.choice(interaction_1_values) if interaction_1_values else 'a',
                Interaction_2_Value=random.choice(interaction_2_values) if interaction_2_values else 'b',
                Interaction_3_Value=random.choice(interaction_3_values) if interaction_3_values else 'c',
                No_of_Replication='1',
                MetaData='Default'
            )
        treatments = Treatment.objects.filter(Experiment_ID=experiment)

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'submit_all':
            new_treatments = []
            for treatment_data in data.get('treatments', []):
                interaction_1_value = treatment_data['interaction_1_value'].strip()
                interaction_2_value = treatment_data['interaction_2_value'].strip()
                interaction_3_value = treatment_data['interaction_3_value'].strip()
                no_of_replication = treatment_data['no_of_replication'].strip()
                metadata = treatment_data['metadata'].strip()

                existing_ids = Treatment.objects.values_list('Treatment_ID', flat=True)
                available_ids = list(set(range(1, 201)) - set(existing_ids))
                treatment_id = random.choice(available_ids)

                logger.debug(f"Creating New Treatment {treatment_id}:")
                logger.debug(f"  Interaction_1_Value: {interaction_1_value}")
                logger.debug(f"  Interaction_2_Value: {interaction_2_value}")
                logger.debug(f"  Interaction_3_Value: {interaction_3_value}")
                logger.debug(f"  No_of_Replication: {no_of_replication}")
                logger.debug(f"  MetaData: {metadata}")

                if not interaction_1_value or not interaction_2_value or not interaction_3_value:
                    logger.error("Found None value(s) in new treatment!")
                    continue

                new_treatments.append(Treatment(
                    Treatment_ID=treatment_id,
                    Experiment_ID=experiment,
                    Interaction_1_Value=interaction_1_value,
                    Interaction_2_Value=interaction_2_value,
                    Interaction_3_Value=interaction_3_value,
                    No_of_Replication=no_of_replication,
                    MetaData=metadata
                ))

            if new_treatments:
                Treatment.objects.bulk_create(new_treatments)
                return JsonResponse({'success': True})

            return JsonResponse({'success': False, 'error': 'No new treatments to add'})

    return render(request, 'show_treatments.html', {'experiment': experiment, 'treatments': treatments})


