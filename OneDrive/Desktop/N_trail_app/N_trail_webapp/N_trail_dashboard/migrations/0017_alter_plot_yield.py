# Generated by Django 5.0.6 on 2024-07-14 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('N_trail_dashboard', '0016_remove_treatment_csv_file_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plot',
            name='Yield',
            field=models.FloatField(),
        ),
    ]
