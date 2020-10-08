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


class LinkerInType(graphene.InputObjectType):
    linker_id = graphene.String()
    concentration = graphene.Decimal()
    plate_number = graphene.Int()
    well = graphene.String()


class Specifications(graphene.Mutation):
    class Arguments:
        specifications = graphene.Argument(SpecificationsType)

    linker_list = graphene.List(graphene.String)

    def mutate(self, info, specifications):
        sbol_document = get_sbol_document(specifications.sbol_string)
        parser = ParserSBOL(sbolDocument=sbol_document)
        list_of_parts = parser.displayListOfParts()
        return Specifications(linker_list=list_of_parts)


class FinalSpec(graphene.Mutation):
    class Arguments:
        linker_types = graphene.List(LinkerInType)
        specifications = graphene.Argument(SpecificationsType)

    output_links = graphene.List(graphene.String)

    def mutate(self, info, linker_types, specifications):

        return FinalSpec(output_links=[str(linker_types), str(specifications)])


class Mutation(graphene.ObjectType):
    run_specifications = Specifications.Field()
    final_spec = FinalSpec.Field()


def get_sbol_document(sbol_string):
    sbol_string_decoded = base64.b64decode(sbol_string)
    doc = Document()
    doc.appendString(sbol_str=sbol_string_decoded, overwrite=True)
    return doc
