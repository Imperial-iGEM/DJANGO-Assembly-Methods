import graphene


class Query(graphene.ObjectType):
    hello_moclo = graphene.String(default_value="Hi From Moclo Assembly")