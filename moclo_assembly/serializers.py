from moclo_assembly.models import MocloModel
from rest_framework import serializers


class MocloSerializer(serializers.ModelSerializer):
    class Meta:
        model = MocloModel
        fields = ['id',
                  'single_triplicate',
                  'dna_plate_map_filename',
                  'combinations_filename',
                  'agar_plate',
                  'python_output',
                  ]