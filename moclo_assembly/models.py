from django.db import models

# Create your models here.
#config = {'output_folder_path': 'output'}
#combinations_limit = 'single'
#dna_plate_map_filename = '/Users/Benedict/Documents/MoClo/OT2-MoClo-Transformation-Ecoli/examples/input_DNA_plate_csv/input-dna-map.csv'
#combinations_filename = '/Users/Benedict/Documents/MoClo/OT2-MoClo-Transformation-Ecoli/examples/combination_to_make_csv/combination-to-make-72.csv'

class MocloModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    single_triplicate = models.CharField(max_length=100)
    dna_plate_map_filename = models.FileField(upload_to="./Moclo_files/input/dna_plate_map", blank=False)
    combinations_filename = models.FileField(upload_to="./Moclo_files/input/combinations", blank=False)
    agar_plate = models.FileField()
    python_output = models.FileField()

    class Meta:
        ordering = ['created']