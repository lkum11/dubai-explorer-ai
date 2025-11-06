import graphene
from graphene import Mutation
from app.graphql.chat_mutations import Mutation as ChatMutation
from app.graphql.user_mutations import Mutation as UserMutations
from app.graphql.queries import Query

class Mutation(ChatMutation, UserMutations, graphene.ObjectType):
    """Aggregates all domain-level mutation groups."""
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
