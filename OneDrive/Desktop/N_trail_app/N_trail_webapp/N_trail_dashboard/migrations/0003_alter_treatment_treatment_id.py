# Generated by Django 5.0.6 on 2024-05-31 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('N_trail_dashboard', '0002_alter_treatment_treatment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treatment',
            name='Treatment_ID',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
