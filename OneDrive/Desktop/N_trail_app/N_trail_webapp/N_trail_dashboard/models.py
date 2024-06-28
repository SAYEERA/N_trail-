from django.db import models
from django.contrib.auth.models import User
import uuid

class Project(models.Model):
    INTERACTION_CHOICES = (
        ('', 'select'),
        ('Timing', 'Timing'),
        ('Inhibitor', 'Inhibitor'),
        ('N_rate', 'N_rate'),
        ('Landscape', 'Landscape'),
        ('Biological', 'Biological'),
        ('Cover_Crop', 'Cover_Crop'),
        ('Crop_Rotation', 'Crop_Rotation'),
        ('Fall_N_Rate', 'Fall_N_Rate'),
        ('Previous_N_Rate', 'Previous_N_Rate'),
        ('Grazing', 'Grazing'),
        ('Spring_N_Rate', 'Spring_N_Rate'),
        ('NA', 'Not Available'),
    )

    

    CROP_CHOICES = (
        ('', 'select'),
        ('NA', 'Not Available'),
        ('Corn', 'Corn'),
        ('Cotton', 'Cotton'),
        ('Rice', 'Rice'),
        ('Fescue', 'Fescue'),
    )
    
    VIEW_TYPE_CHOICES = (
        ('', 'select'),
        ('public', 'Public'),
        ('protected', 'Protected'),
    )


    Project_ID = models.CharField(max_length=120, primary_key=True)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    # Start_year = models.IntegerField(default=2022)
    Interactions_count = models.IntegerField(default=0)
    Interaction_1 = models.CharField(max_length=120, blank=True, null=True)
    Interaction_2 = models.CharField(max_length=120, blank=True, null=True)
    Interaction_3 = models.CharField(max_length=120, blank=True, null=True)
    Crop = models.CharField(max_length=50, choices=CROP_CHOICES, default='NA')
    # No_of_Year = models.IntegerField(default=1)
    Project_Editors = models.CharField(max_length=100,  default='NA')
    Funding_Source = models.CharField(max_length=100, default='Unknown')
    MetaData = models.TextField(default='No metadata available')
    View_Type = models.CharField(max_length=10, choices=VIEW_TYPE_CHOICES, default='private')

    def __str__(self):
        return self.Project_ID

class Location(models.Model):
    Location_ID     = models.CharField('Location_ID', max_length=120, blank=False, null=False, primary_key=True)
    State           = models.CharField('State', max_length=120, blank=False, null=False)
    County          = models.CharField('County', max_length=120, blank=False, null=False) 
    Owner           = models.CharField('Owner', max_length=120, blank=False, null=False)
    Latitude        = models.CharField('Latitude', max_length=120, blank=False, null=False)
    Longitude       = models.CharField('Longitude', max_length=120, blank=False, null=False)
    Contact         = models.CharField('Contact', max_length=120, blank=False, null=False)
    MetaData        = models.TextField('MetaData', max_length=120, blank=False, null=False)
     
    def __str__(self):
        return self.Location_ID


class Experiment(models.Model):
    LOCATION_CHOICES = (
        ('Select', 'select'),
        ('other', 'other'),
        ('GRC', 'GRC'),
        ('BRC', 'BRC'),
        ('FDRC', 'FDRC'),
    )

    Experiment_ID = models.CharField('Experiment_ID', max_length=120, blank=False, null=False, primary_key=True)
    Project_ID = models.ForeignKey(Project, on_delete=models.CASCADE)
    Location_ID = models.ForeignKey(Location, on_delete=models.CASCADE)
    Year = models.CharField('Year', max_length=120, blank=False, null=False)
    Interaction_1_count = models.IntegerField(default=0)
    Interaction_1_value = models.TextField(default="")
    Interaction_2_count = models.IntegerField(default=0)
    Interaction_2_value = models.TextField(default="")
    Interaction_3_count = models.IntegerField(default=0)
    Interaction_3_value = models.TextField(default="")
    Yield_Map = models.JSONField(default=list, blank=True, null=True)
    Soil_Sample = models.TextField('Soil_Sample', blank=True, null=True)
    Sonic_sensor = models.JSONField(default=list, blank=True, null=True)
    GCP = models.JSONField(default=list, blank=True, null=True)
    RAWUAV = models.JSONField(default=list, blank=True, null=True)
    Orthomosic_UAV = models.JSONField(default=list, blank=True, null=True)
    DSM_UAV = models.JSONField(default=list, blank=True, null=True)
    Orthomosic_SAT = models.JSONField(default=list, blank=True, null=True)
    DSM_SAT = models.CharField(max_length=255, blank=True, null=True)
    VI_1 = models.JSONField(default=list, blank=True, null=True)
    VI_2 = models.JSONField(default=list, blank=True, null=True)
    VI_3 = models.JSONField(default=list, blank=True, null=True)
    MetaData = models.TextField('MetaData', max_length=120, blank=False, null=False)

    def __str__(self):
        return self.Experiment_ID

class Treatment(models.Model):
    Treatment_ID = models.CharField(max_length=50, primary_key=True)
    Experiment_ID = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    Interaction_1_Value = models.CharField('Interaction_1_Value', max_length=120, blank=False, null=False)
    Interaction_2_Value = models.CharField('Interaction_2_Value', max_length=120, blank=False, null=False)
    Interaction_3_Value = models.CharField('Interaction_3_Value', max_length=120, blank=False, null=False)
    No_of_Replication = models.CharField('No_of_Replication', max_length=120, blank=False, null=False)
    MetaData = models.TextField('MetaData', max_length=120, blank=False, null=False)

    def __str__(self):
        return self.Treatment_ID

class Plot(models.Model):
    Treatment_ID = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    Replication_ID = models.IntegerField()
    Plot_ID = models.CharField(max_length=120)
    Yield = models.CharField(max_length=120)
    Units = models.CharField('Units', max_length=120, blank=True, null=True)

    class Meta:
        unique_together = (('Treatment_ID', 'Replication_ID'),)

    def __str__(self):
        return f"Treatment: {self.Treatment_ID}, Replication: {self.Replication_ID}"
    