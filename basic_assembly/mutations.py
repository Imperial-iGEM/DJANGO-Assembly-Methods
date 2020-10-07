import graphene
from graphene_django import DjangoObjectType
from basic_assembly.models import BasicModel as BasicModel


class ExampleType(DjangoObjectType):
    class Meta:
        model = BasicModel


class Example(graphene.Mutation):
    class Arguments:
        example_arg = graphene.String()

    example_arg = graphene.Field(ExampleType)

    def mutate(self, example_arg):
        pass


class Mutation(graphene.ObjectType):
    example_arg = Example.Field()