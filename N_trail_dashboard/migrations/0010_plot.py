# Generated by Django 5.0.6 on 2024-06-16 04:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('N_trail_dashboard', '0009_alter_experiment_dsm_sat_alter_experiment_dsm_uav_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Replication_ID', models.IntegerField()),
                ('Plot_ID', models.CharField(max_length=120)),
                ('Treatment_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='N_trail_dashboard.treatment')),
            ],
            options={
                'unique_together': {('Treatment_ID', 'Replication_ID')},
            },
        ),
    ]
