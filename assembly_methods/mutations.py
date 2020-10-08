import graphene
from graphene_django import DjangoObjectType
from .models import LinkerModel


class Specifications(graphene.Mutation):
    class Arguments:
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

    linker_list = graphene.List()

    def mutate(self, sbol_string, liquid_handler,
               remove_repeated,
               number_of_wells,
               number_of_runs,
               output_plate_positions,
               output_reagents_list,
               output_part_sequences,
               output_logs,
               output_meta_information):

        return Specifications(linker_list=["Test link 1", "Test link 2"])


class LinkerInType(DjangoObjectType):
    class Meta:
        model = LinkerModel


class FinalSpec(graphene.Mutation):
    class Arguments:
        linker_types = graphene.Field(LinkerInType)
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

    output_links = graphene.List()

    def mutate(self, linker_types, sbol_string, liquid_handler,
               remove_repeated,
               number_of_wells,
               number_of_runs,
               output_plate_positions,
               output_reagents_list,
               output_part_sequences,
               output_logs,
               output_meta_information):

        return FinalSpec(output_links=["Test link 1", "Test link 2"])


class Mutation(graphene.ObjectType):
    run_specifications = Specifications.Field()
    final_spec = FinalSpec.Field()
