from django.db import models
from django.contrib.auth.models import User
import uuid

class Project(models.Model):
    INTERACTION_CHOICES = (
        ('Select', 'select'),
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
        ('Select', 'select'),
        ('NA', 'Not Available'),
        ('Corn', 'Corn'),
        ('Cotton', 'Cotton'),
        ('Rice', 'Rice'),
        ('Fescue', 'Fescue'),
    )

    PROJECT_ROLE_CHOICES = (
        ('Select', 'select'),
        ('Researcher', 'Researcher'),
        ('Manager', 'Manager'),
        ('Administrator', 'Administrator'),
    )

    Project_ID = models.CharField(max_length=120, primary_key=True)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    Start_year = models.IntegerField(default=2022)
    Interactions_count = models.IntegerField(default=0)
    Interaction_1 = models.CharField(max_length=120, blank=True, null=True)
    Interaction_2 = models.CharField(max_length=120, blank=True, null=True)
    Interaction_3 = models.CharField(max_length=120, blank=True, null=True)
    Crop = models.CharField(max_length=50, choices=CROP_CHOICES, default='NA')
    No_of_Year = models.IntegerField(default=1)
    Role = models.CharField(max_length=100, choices=PROJECT_ROLE_CHOICES, default='Researcher')
    Funding_Source = models.CharField(max_length=100, default='Unknown')
    MetaData = models.TextField(default='No metadata available')

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
        ('NA', 'Not Available'),
        ('GRC', 'GRC'),
        ('BRC', 'BRC'),
        ('FDRC', 'FDRC'),
    )

    Experiment_ID           = models.CharField('Experiment_ID', max_length=120, blank=False, null=False, primary_key=True)
    Project_ID              = models.ForeignKey(Project, on_delete=models.CASCADE)
    Location_ID             = models.ForeignKey(Location, on_delete=models.CASCADE) 
    Year                    = models.CharField('Year', max_length=120, blank=False, null=False)
    Interaction_1_count     = models.IntegerField('Interaction_1_count', blank=True, null=True, default=0)
    Interaction_1_count_1   = models.CharField('Interaction_1_count_1', max_length=120, default='NA')
    Interaction_1_count_2   = models.CharField('Interaction_1_count_2', max_length=120, default='NA')
    Interaction_1_count_3   = models.CharField('Interaction_1_count_3', max_length=120, default='NA')
    Interaction_1_count_4   = models.CharField('Interaction_1_count_4', max_length=120, default='NA')
    Interaction_1_count_5   = models.CharField('Interaction_1_count_5', max_length=120, default='NA')
    Interaction_2_count     = models.IntegerField('Interaction_2_count', blank=True, null=True, default=0)
    Interaction_2_count_1   = models.CharField('Interaction_2_count_1', max_length=120, default='NA')
    Interaction_2_count_2   = models.CharField('Interaction_2_count_2', max_length=120, default='NA')
    Interaction_2_count_3   = models.CharField('Interaction_2_count_3', max_length=120, default='NA')
    Interaction_2_count_4   = models.CharField('Interaction_2_count_4', max_length=120, default='NA')
    Interaction_2_count_5   = models.CharField('Interaction_2_count_5', max_length=120, default='NA')
    Interaction_3_count     = models.IntegerField('Interaction_3_count', blank=True, null=True, default=0)
    Interaction_3_count_1   = models.CharField('Interaction_3_count_1', max_length=120, default='NA')
    Interaction_3_count_2   = models.CharField('Interaction_3_count_2', max_length=120, default='NA')
    Interaction_3_count_3   = models.CharField('Interaction_3_count_3', max_length=120, default='NA')
    Interaction_3_count_4   = models.CharField('Interaction_3_count_4', max_length=120, default='NA')
    Interaction_3_count_5   = models.CharField('Interaction_3_count_5', max_length=120, default='NA')
    MetaData                = models.TextField('MetaData', max_length=120,blank=False, null=False)
    
    def __str__(self):
        return self.Experiment_ID
    
class Treatment(models.Model):
    Treatment_ID            = models.IntegerField(primary_key=True)
    Experiment_ID           = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    Interaction_1_Value     = models.CharField('Interaction_1_Value', max_length=120, blank=False, null=False)
    Interaction_2_Value     = models.CharField('Interaction_2_Value', max_length=120, blank=False, null=False)
    Interaction_3_Value     = models.CharField('Interaction_3_Value', max_length=120, blank=False, null=False)
    No_of_Replication       = models.CharField('No_of_Replication', max_length=120, blank=False, null=False)
    MetaData                = models.TextField('MetaData', max_length=120, blank=False, null=False)
    
    def __str__(self):
        return str(self.Treatment_ID)
    