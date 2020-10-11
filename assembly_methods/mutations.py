import graphene
from sbol_parser_api.sbolParserApi import ParserSBOL

import base64
from sbol2 import Document


class SpecificationsType(graphene.InputObjectType):
    sbol_string = graphene.String()
    liquid_handler = graphene.String()
    remove_repeated = graphene.Boolean()
    number_of_wells = graphene.Int()
    number_of_runs = graphene.Int()
    output_plate_positions = graphene.Boolean()
    output_reagents_list = graphene.Boolean()
    output_part_sequences = graphene.Boolean()
    output_logs = graphene.Boolean()
    output_meta_information = graphene.Boolean()
    assembly_type = graphene.String()


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
        specifications = graphene.Argument(SpecificationsType)

    # output
    output_links = graphene.List(graphene.String)

    # Function that is run: call other functions from here
    def mutate(self, info, linker_types, specifications):
        sbol_document = get_sbol_document(specifications.sbol_string)
        parser = ParserSBOL(sbolDocument=sbol_document)
        if specifications.assembly_type == "basic":
            links = parser.generateCsv_for_DNABot()
        elif specifications.assembly_type == "golden_gate":
            links = parser.generateCsv_for_BioBricks()
        elif specifications.assembly_type == "moclo":
            link = parser.generateCsv_for_MoClo()
        # return classes with outputs
        return FinalSpec(output_links=[str(linker_types), str(specifications)])


class Mutation(graphene.ObjectType):
    linker_list = LinkerList.Field()
    final_spec = FinalSpec.Field()


def get_sbol_document(sbol_string):
    sbol_string_decoded = base64.b64decode(sbol_string)
    doc = Document()
    doc.appendString(sbol_str=sbol_string_decoded, overwrite=True)
    return doc
