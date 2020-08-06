from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, generics
from .serializers import BasicSerializer

from rest_framework.decorators import action
from rest_framework.response import Response

from .dna_bot.dnabot_app import dnabot

from .models import BasicModel

import os

# Create your views here.


class BasicView(viewsets.ModelViewSet):
    queryset = BasicModel.objects.all()
    serializer_class = BasicSerializer

    def create(self, request, *args, **kwargs):
        input_data = request.data
        new_input = BasicModel.objects.create(
            ethanol_stage2=input_data["ethanol_stage2"],
            deep_well_stage4=input_data["deep_well_stage4"],
            construct_csv=input_data["construct_csv"],
            parts_linkers_csv=input_data["parts_linkers_csv"])

        #new_input.save()
        print(new_input)
        serializer = BasicSerializer(new_input)
        print(serializer.data['construct_csv'])
        print(serializer.data['parts_linkers_csv'])

        half_file_path_of_construct = serializer.data['construct_csv']
        half_file_path_of_parts = serializer.data['parts_linkers_csv']
        ethanol2 = serializer.data['ethanol_stage2']
        deep4 = serializer.data['deep_well_stage4']

        full_construct_path = os.path.abspath(half_file_path_of_construct)
        full_parts_path = os.path.abspath(half_file_path_of_parts)

        full_parts_paths = []
        full_parts_paths.append(full_parts_path)

        all_outputs = dnabot(ethanol2, deep4, full_construct_path, full_parts_paths)
        print(all_outputs)

        Full_information_new_input = BasicModel.objects.create(
            ethanol_stage2=input_data["ethanol_stage2"],
            deep_well_stage4=input_data["deep_well_stage4"],
            construct_csv=input_data["construct_csv"],
            parts_linkers_csv=input_data["parts_linkers_csv"],
            python_output_1 = all_outputs[0],
            python_output_2 = all_outputs[1],
            python_output_3 = all_outputs[2],
            python_output_4 = all_outputs[3])

        Full_information_new_input.save()
        Full_info_serializer = BasicSerializer(Full_information_new_input)
        return Response(Full_info_serializer.data)