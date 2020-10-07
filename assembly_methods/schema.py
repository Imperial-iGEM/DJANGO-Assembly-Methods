import graphene

import basic_assembly.schema
import basic_assembly.mutations
import biobricks_assembly.schema
import biobricks_assembly.mutations
import moclo_assembly.schema
import moclo_assembly.mutations

class Query(
    basic_assembly.schema.Query,
    biobricks_assembly.schema.Query,
    moclo_assembly.schema.Query,


):
    pass


class Mutation(
    basic_assembly.mutations.Mutation,
    # biobricks_assembly.mutations.Mutation,
    moclo_assembly.mutations.Mutation,

):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
