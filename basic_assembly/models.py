from django.db import models

# Create your models here.


class BasicModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    ethanol_stage2 = models.CharField(max_length=100)
    deep_well_stage4 = models.CharField(max_length=100)
    construct_csv = models.FileField(upload_to="./basic_files/input/constructs", blank=False)
    parts_linkers_csv = models.FileField(upload_to="./basic_files/input/parts_linkers", blank=False)
    python_output_1 = models.FileField()
    python_output_2 = models.FileField()
    python_output_3 = models.FileField()
    python_output_4 = models.FileField()

    class Meta:
        ordering = ['created']