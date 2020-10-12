import graphene
from sbol_parser_api.sbolParserApi import ParserSBOL
import base64
from sbol2 import Document
from basic_assembly.dna_bot import dnabot_app

class BasicLabware(graphene.InputObjectType):
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
    basic_labware = graphene.Argument(BasicLabware)
    reagent_plate = graphene.String()
    mag_plate = graphene.String()
    tube_rack = graphene.String()
    aluminum_block = graphene.String()
    bead_container = graphene.String()
    soc_plate = graphene.String()
    agar_plate = graphene.String()


class InputSpecsBASIC(graphene.InputObjectType):
    output_folder = graphene.String()
    ethanol_well_for_stage_2 = graphene.String()
    deep_well_plate_stage_4 = graphene.String()
    input_construct_path = graphene.String()
    output_sources_path = graphene.List(graphene.String())
    labware_dict = graphene.Argument(LabwareDictBASIC)


class LabwareDictMoClo(graphene.InputObjectType):
    basic_labware = graphene.Argument(BasicLabware)
    well_plate = graphene.String()
    trough = graphene.String()
    reagent_plate = graphene.String()
    agar_plate = graphene.String()


class InputSpecsMoClo(graphene.InputObjectType):
    output_folder = graphene.String()
    construct_path = graphene.String()
    part_path = graphene.String()
    thermocycle = graphene.Boolean()
    labware_dict = graphene.Argument(LabwareDictMoClo)


class LabwareDictBioBricks(graphene.InputObjectType):
    basic_labware = graphene.Argument(BasicLabware)
    tube_rack = graphene.String()
    soc_plate = graphene.String()
    transformation_plate = graphene.String()


class InputSpecsBioBricks(graphene.InputObjectType):
    output_folder = graphene.String()
    construct_path = graphene.String()
    part_path = graphene.String()
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
        parser = ParserSBOL(sbolDocument=sbol_document)
        if assembly_type == "basic":
            csv_links = parser.generateCsv_for_DNABot()
            links = dnabot_app.dnabot()
        elif assembly_type == "golden_gate":
            csv_links = parser.generateCsv_for_BioBricks()
        elif assembly_type == "moclo":
            csv_links = parser.generateCsv_for_MoClo()
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
