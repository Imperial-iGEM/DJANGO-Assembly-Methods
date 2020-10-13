import os

import graphene
from django.conf.global_settings import MEDIA_ROOT
from datetime import datetime
from sbol_parser_api.sbolParserApi import ParserSBOL
import base64
from sbol2 import Document
from basic_assembly.dna_bot import dnabot_app
from biobricks_assembly.biobricks10 import bbinput
from moclo_assembly.moclo_transformation import moclo_transform_generator


class CommonLabware(graphene.InputObjectType):
    p10_mount = graphene.String()
    p300_mount = graphene.String()
    p10_type = graphene.String()
    p300_type = graphene.String()
    well_plate = graphene.String()


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
        part_types_dictionary = convert_part_info(linker_types)
        parser = ParserSBOL(sbolDocument=sbol_document, outdir=output_folder)
        if assembly_type == "basic":
            csv_links = parser.generateCsv_for_DNABot(dictOfParts=part_types_dictionary)
            labware_dict = specifications_basic.labware_dict
            common_labware = labware_dict.common_labware
            links = dnabot_app.dnabot(output_folder=output_folder,
                                      ethanol_well_for_stage_2=specifications_basic.ethanol_well_for_stage_2,
                                      deep_well_plate_stage_4=specifications_basic.deep_well_plate_stage_4,
                                      input_construct_path=csv_links['construct_path'],
                                      output_sources_paths=csv_links['part_path'],
                                      p10_mount=common_labware.p10_mount,
                                      p300_mount=common_labware.p300_mount,
                                      p10_type=common_labware.p10_type,
                                      p300_type=common_labware.p300_type,
                                      well_plate=common_labware.well_plate,
                                      reagent_plate=labware_dict.reagent_plate,
                                      mag_plate=labware_dict.mag_plate,
                                      tube_rack=labware_dict.tube_rack,
                                      aluminum_block=labware_dict.aluminum_block,
                                      bead_container=labware_dict.bead_container,
                                      soc_plate=labware_dict.soc_plate,
                                      agar_plate=labware_dict.agar_plate
                                      )
        elif assembly_type == "bio_bricks":
            labware_dict = specifications_bio_bricks.labware_dict
            common_labware = labware_dict.common_labware
            csv_links = parser.generateCsv_for_BioBricks(dictOfParts=part_types_dictionary)
            links = bbinput.biobricks(output_folder=output_folder,
                                      construct_path=csv_links["construct_path"],
                                      part_path=csv_links["part_path"],
                                      thermocycle=specifications_bio_bricks.thermocycle,
                                      p10_mount=common_labware.p10_mount,
                                      p300_mount=common_labware.p300_mount,
                                      p10_type=common_labware.p10_type,
                                      p300_type=common_labware.p300_type,
                                      well_plate=common_labware.well_plate,
                                      tube_rack=labware_dict.tube_rack,
                                      soc_plate=labware_dict.soc_plate,
                                      transformation_plate=labware_dict.transformation_plate
                                      )
        elif assembly_type == "moclo":
            labware_dict = specifications_bio_bricks.labware_dict
            common_labware = labware_dict.common_labware
            csv_links = parser.generateCsv_for_MoClo(dictOfParts=part_types_dictionary)
            links = moclo_transform_generator.moclo_function(
                output_folder=output_folder,
                construct_path=csv_links["construct_path"],
                part_path=csv_links["part_path"],
                thermocycle=specifications_bio_bricks.thermocycle,
                p10_mount=common_labware.p10_mount,
                p300_mount=common_labware.p300_mount,
                p10_type=common_labware.p10_type,
                p300_type=common_labware.p300_type,
                well_plate=common_labware.well_plate,
                trough=labware_dict.trough,
                reagent_plate=labware_dict.reagent_plate,
                agar_plate=labware_dict.agar_plate
            )
        else:
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


def convert_part_info(part_types_list):
    return {
        part_type.linker_id: {
            "concentration": part_type.concentration,
            "plate": part_type.plate_number,
            "well": part_type.well
        } for part_type in part_types_list}
