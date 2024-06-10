
# N_trail_dashboard/admin.py
from django.contrib import admin
from .models import Project
from .models import Location
from .models import Experiment
from .models import Treatment

admin.site.site_header = 'N_trail Admin_Dashboard_'

# code to change admin area display
## show all the columns
@admin.register(Project)
class project_admin(admin.ModelAdmin):
    list_display=('Project_ID','User_ID', 'Start_year','Interactions_count','Interaction_1',
                  'Interaction_2','Interaction_3','Crop','No_of_Year','Project_Editors','Funding_Source','MetaData')

@admin.register(Location)
class location_admin(admin.ModelAdmin):
    list_display = ('Location_ID','State','County', 'Owner', 'Latitude', 'Longitude', 'Contact', 'MetaData')

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        'Experiment_ID', 'Project_ID', 'Location_ID', 'Year',
        'Interaction_1_count', 'Interaction_1_value',
        'Interaction_2_count', 'Interaction_2_value',
        'Interaction_3_count', 'Interaction_3_value',
        'Yield_Map', 'Soil_Sample', 'Sonic_sensor', 'GCP', 'RAWUAV',
        'Orthomosic_UAV', 'DSM_UAV', 'Orthomosic_SAT', 'DSM_SAT', 
        'VI_1', 'VI_2', 'VI_3', 'MetaData'
    )

    
                        
@admin.register(Treatment)
class treatment_admin(admin.ModelAdmin):
    list_display=('Treatment_ID','Experiment_ID','Interaction_1_Value','Interaction_2_Value',
                  'Interaction_3_Value', 'No_of_Replication', 'MetaData')

            
                