import graphene


class Query(graphene.ObjectType):
    hello_biobricks = graphene.String(default_value="Hi From Bio Bricks Assembly")