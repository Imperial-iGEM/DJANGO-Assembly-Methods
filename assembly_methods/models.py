from django.db import models


class LinkerModel(models.Model):
    linker_id = models.CharField(null=False, default="")
    concentration = models.DecimalField(null=False, default=1)
    plate_number = models.IntegerField(null=False, default=0)
    well = models.CharField(null=False, default="")