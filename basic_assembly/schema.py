import graphene


class Query(graphene.ObjectType):
    hello_basic = graphene.String(default_value="Hi From Basic Assembly")