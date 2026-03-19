import graphene
from graphene import Mutation, ObjectType, Field, List, Int, String
from app.graphql.gql_objects import UserType
from app.graphql.chat_mutations import Mutation as ChatMutation
from app.graphql.user_mutations import Mutation as UserMutations
from app.graphql.resolvers.rag_resolver import resolve_askRAG
from app.graphql.resolvers.user_resolver import resolve_user, resolve_users

class Mutation(ChatMutation, UserMutations, graphene.ObjectType):
    """Aggregates all domain-level mutation groups."""
    pass

class Query(ObjectType):
    users = List(UserType)
    user = Field(UserType, id=Int(required=True))
    askRAG = Field(
        String,
        query_text=String(required=True),
        description="Ask a question about Dubai attractions using RAG pipeline."
    )

    resolve_users = resolve_users
    resolve_user = resolve_user
    resolve_askRAG = resolve_askRAG

schema = graphene.Schema(query=Query, mutation=Mutation)
