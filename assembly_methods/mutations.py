import os

import graphene
from django.conf.global_settings import MEDIA_ROOT
from datetime import datetime
from sbol_parser_api.sbolParserApi import ParserSBOL
import base64
from sbol2 import Document
from basic_assembly.dna_bot import dnabot_app


class CommonLabware(graphene.InputObjectType):
    p10_mount = graphene.String()
    p300_mount = graphene.String()
    p10_type = graphene.String()
    p300_type = graphene.String()


class SpecificationsType(graphene.InputObjectType):
    sbol_string = graphene.String()
    liquid_handler = graphene.String()
    remove_repeated = graphene.Boolean()
    assembly_type = graphene.String()


class LabwareDictBASIC(graphene.InputObjectType):
    common_labware = graphene.Argument(CommonLabware)
    well_plate = graphene.String()
    reagent_plate = graphene.String()
    mag_plate = graphene.String()
    tube_rack = graphene.String()
    aluminum_block = graphene.String()
    bead_container = graphene.String()
    soc_plate = graphene.String()
    agar_plate = graphene.String()


class InputSpecsBASIC(graphene.InputObjectType):
    ethanol_well_for_stage_2 = graphene.String()
    deep_well_plate_stage_4 = graphene.String()
    labware_dict = graphene.Argument(LabwareDictBASIC)


class LabwareDictMoClo(graphene.InputObjectType):
    common_labware = graphene.Argument(CommonLabware)
    well_plate = graphene.String()
    trough = graphene.String()
    reagent_plate = graphene.String()
    agar_plate = graphene.String()


class InputSpecsMoClo(graphene.InputObjectType):
    thermocycle = graphene.Boolean()
    labware_dict = graphene.Argument(LabwareDictMoClo)


class LabwareDictBioBricks(graphene.InputObjectType):
    common_labware = graphene.Argument(CommonLabware)
    tube_rack = graphene.String()
    soc_plate = graphene.String()
    transformation_plate = graphene.String()


class InputSpecsBioBricks(graphene.InputObjectType):
    thermocycle = graphene.Boolean()
    labware_dict = graphene.Argument(LabwareDictBioBricks)


class LinkerInType(graphene.InputObjectType):
    linker_id = graphene.String()
    concentration = graphene.Decimal()
    plate_number = graphene.Int()
    well = graphene.String()


class LinkerList(graphene.Mutation):
    class Arguments:
        sbol_file_string = graphene.String()
        # specifications = graphene.Argument(SpecificationsType)

    linker_list = graphene.List(graphene.String)

    def mutate(self, info, sbol_file_string):
        sbol_document = get_sbol_document(sbol_file_string)
        parser = ParserSBOL(sbolDocument=sbol_document)
        list_of_parts = parser.displayListOfParts()
        return LinkerList(linker_list=list_of_parts)


class FinalSpec(graphene.Mutation):
    class Arguments:
        # Input args
        linker_types = graphene.List(LinkerInType)
        assembly_type = graphene.String()
        sbol_file_string = graphene.String()
        specifications_basic = graphene.Argument(InputSpecsBASIC)
        specifications_bio_bricks = graphene.Argument(InputSpecsBioBricks)
        specifications_mo_clo = graphene.Argument(InputSpecsMoClo)

    # output
    output_links = graphene.List(graphene.String)

    # Function that is run: call other functions from here
    def mutate(self, info, linker_types, assembly_type, sbol_file_string, specifications_basic,
               specifications_bio_bricks, specifications_mo_clo):
        sbol_document = get_sbol_document(sbol_file_string)
        date_time = "{:%Y%m%d_%H_%M_%S}".format(datetime.now())
        output_folder = os.path.join(MEDIA_ROOT, date_time)
        os.mkdir(output_folder)
        parser = ParserSBOL(sbolDocument=sbol_document, out_dir=output_folder)
        if assembly_type == "basic":
            csv_links = parser.generateCsv_for_DNABot()
            labware_dict = specifications_basic.labware_dict
            common_labware = labware_dict.common_labware
            links = dnabot_app.dnabot(full_output_path=output_folder,
                                      ethanol_well_for_stage_2=specifications_basic.ethanol_well_for_stage_2,
                                      deep_well_plate_stage_4=specifications_basic.deep_well_plate_stage_4,
                                      input_construct_path=csv_links['input_construct_path'],
                                      output_sources_paths=csv_links['output_sources_paths'],
                                      p10_mount=common_labware.p10_mount,
                                      p300_mount=common_labware.p300_mount,
                                      p10_type=common_labware.p10_type,
                                      p300_type=common_labware.p300_type,
                                      well_plate=labware_dict.well_plate,
                                      reagent_plate=labware_dict.reagent_plate,
                                      mag_plate=labware_dict.mag_plate,
                                      tube_rack=labware_dict.tube_rack,
                                      aluminum_block=labware_dict.aluminum_block,
                                      bead_container=labware_dict.bead_container,
                                      soc_plate=labware_dict.soc_plate,
                                      agar_plate=labware_dict.agar_plate
                                      )
        elif assembly_type == "golden_gate":
            csv_links = parser.generateCsv_for_BioBricks()
            links = []
        elif assembly_type == "moclo":
            csv_links = parser.generateCsv_for_MoClo()
            links = []
        # return classes with outputs
        return FinalSpec(output_links=links)


class Mutation(graphene.ObjectType):
    linker_list = LinkerList.Field()
    final_spec = FinalSpec.Field()


def get_sbol_document(sbol_string):
    sbol_string_decoded = base64.b64decode(sbol_string)
    doc = Document()
    doc.appendString(sbol_str=sbol_string_decoded, overwrite=True)
    return doc
