# Generated by Django 5.0.6 on 2024-06-14 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('N_trail_dashboard', '0005_remove_project_role_project_project_editors'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='View_Type',
            field=models.CharField(choices=[('private', 'Private'), ('protected', 'Protected')], default='private', max_length=10),
        ),
    ]
