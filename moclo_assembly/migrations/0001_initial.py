# Generated by Django 3.1 on 2020-08-06 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MocloModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('single_triplicate', models.CharField(max_length=100)),
                ('dna_plate_map_filename', models.FileField(upload_to='./Moclo_files/input/dna_plate_map')),
                ('combinations_filename', models.FileField(upload_to='./Moclo_files/input/combinations')),
                ('agar_plate', models.FileField(upload_to='')),
                ('python_output', models.FileField(upload_to='')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
