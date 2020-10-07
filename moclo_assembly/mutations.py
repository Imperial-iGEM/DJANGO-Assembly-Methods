import graphene
from graphene_django import DjangoObjectType
from moclo_assembly.models import MocloModel as MocloModel


class ExampleType(DjangoObjectType):
    class Meta:
        model = MocloModel


class Example(graphene.Mutation):
    class Arguments:
        example_arg = graphene.String()

    example_arg = graphene.Field(ExampleType)

    def mutate(self, example_arg):
        pass


class Mutation(graphene.ObjectType):
    example_arg = Example.Field()