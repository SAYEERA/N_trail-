
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
                  'Interaction_2','Interaction_3','Crop','No_of_Year','Role','Funding_Source','MetaData')

@admin.register(Location)
class location_admin(admin.ModelAdmin):
    list_display = ('Location_ID','State','County', 'Owner', 'Latitude', 'Longitude', 'Contact', 'MetaData')

@admin.register(Experiment)
class experement_admin(admin.ModelAdmin):
    list_display = ('Experiment_ID','Project_ID','Location_ID','Year',
                    'Interaction_1_count','Interaction_1_count_1','Interaction_1_count_2','Interaction_1_count_3','Interaction_1_count_4','Interaction_1_count_5',
                    'Interaction_2_count','Interaction_2_count_1','Interaction_2_count_2','Interaction_2_count_3','Interaction_2_count_4','Interaction_2_count_5',
                    'Interaction_3_count','Interaction_3_count_1','Interaction_3_count_2','Interaction_3_count_3','Interaction_3_count_4','Interaction_3_count_5',
                    'MetaData',)
                        
@admin.register(Treatment)
class treatment_admin(admin.ModelAdmin):
    list_display=('Treatment_ID','Experiment_ID','Interaction_1_Value','Interaction_2_Value',
                  'Interaction_3_Value', 'No_of_Replication', 'MetaData')

            
                