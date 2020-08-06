from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, generics
from .serializers import MocloSerializer

from rest_framework.decorators import action
from rest_framework.response import Response

from .moclo_transformation.moclo_transform_generator import moclo_function

from .models import MocloModel

import os
import random
import string

# Create your views here.


class MocloView(viewsets.ModelViewSet):
    queryset = MocloModel.objects.all()
    serializer_class = MocloSerializer
    
    def create(self, request, *args, **kwargs):
        input_data = request.data
        new_input = MocloModel.objects.create(
            single_triplicate=input_data["single_triplicate"],
            dna_plate_map_filename=input_data["dna_plate_map_filename"],
            combinations_filename=input_data["combinations_filename"])

        #new_input.save()
        print(new_input)
        serializer = MocloSerializer(new_input)
        print(serializer.data['dna_plate_map_filename'])
        print(serializer.data['combinations_filename'])

        half_file_path_of_dna_plate = serializer.data['dna_plate_map_filename']
        half_file_path_of_combinations = serializer.data['combinations_filename']
        single_triplicate_string = serializer.data['single_triplicate']

        full_dna_path = os.path.abspath(half_file_path_of_dna_plate)
        full_combinations_path = os.path.abspath(half_file_path_of_combinations)

        #full_parts_paths = []
        #full_parts_paths.append(full_parts_path)
        output = 'Moclo_files/output'
        random = get_random_string(20)
        file_output_path = os.path.join(output,random)
        agar_path = os.path.join(os.path.abspath(file_output_path), 'Agar_plate.csv')
        python_path = os.path.join(os.path.abspath(file_output_path), 'moclo_transform_protocol.py')
        moclo_function(file_output_path, single_triplicate_string, full_dna_path, full_combinations_path)
        #print(all_outputs)

        Full_information_new_input = MocloModel.objects.create(
            single_triplicate=input_data["single_triplicate"],
            dna_plate_map_filename=input_data["dna_plate_map_filename"],
            combinations_filename=input_data["combinations_filename"],
            agar_plate = agar_path,
            python_output = python_path)

        Full_information_new_input.save()
        Full_info_serializer = MocloSerializer(Full_information_new_input)
        return Response(Full_info_serializer.data)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    #print("Random string of length", length, "is:", result_str)
    return result_str