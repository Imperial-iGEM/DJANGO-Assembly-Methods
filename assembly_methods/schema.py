import graphene

import basic_assembly.schema
import basic_assembly.mutations
import biobricks_assembly.schema
import biobricks_assembly.mutations
import moclo_assembly.schema
import moclo_assembly.mutations


class Query(graphene.ObjectType):
    hello_biobricks = graphene.String(default_value="Hi From Bio Bricks Assembly")

