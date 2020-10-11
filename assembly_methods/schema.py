import graphene
from .mutations import Mutation


class Query(graphene.ObjectType):
    hello_biobricks = graphene.String(default_value="Hi From Bio Bricks Assembly")


schema = graphene.Schema(query=Query, mutation=Mutation)
