import graphene
from graphene import ObjectType, Field, Int, String, Mutation
from app.models import User
from app.db import db
from app.graphql.gql_objects import UserType


class UserMutations(Mutation):
    class Arguments:
        username = String(required=True)
        email = String(required=True)
        bio = String()

    ok = graphene.Boolean()
    user = Field(UserType)

    def mutate(self, info, username, email, bio=None):
        user = User(username=username, email=email, bio=bio)
        db.session.add(user)
        db.session.commit()
        return UserMutations(ok=True, user=user)

class Mutation(ObjectType):
    create_user = UserMutations.Field()

schema = graphene.Schema(mutation=Mutation)
