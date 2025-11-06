import graphene
from graphene import ObjectType, String, Mutation, Boolean, List
from app.chatbot.chat_openai import openai_chat_response
from app.chatbot.chat_system import chat_system_response
from app.chatbot.utils import clear_chat_history, get_chat_history


class ChatMutation(Mutation):
    """Handles chatbot interaction via OpenAI or system context."""
    class Arguments:
        user_input = String(required=True)
    
    response = String()
    def mutate(self, info, user_input):
        try:
            # res = openai_chat_response(user_input=user_input)
            res = chat_system_response(user_input=user_input, user_id="test_user_1")
            return ChatMutation(response=res)
        # TODO: Learn basic exception handling a lead should know
        except ValueError as e:
            return ChatMutation(response=f"Input error: {e}")
        except Exception as ex:
            return ChatMutation(response="Internal server error")


class ClearChatMutation(Mutation):
    """clear past chatbot interaction via OpenAI or system context."""
    class Arguments:
        user_id = String(required=True)

    response = Boolean()
    def mutate(self, info, user_id):
        try:
            result = clear_chat_history(user_id)
            return ClearChatMutation(response=result)
        except Exception as ex:
            return ClearChatMutation(response=False)


class GetChatHistoryMutation(Mutation):
    """fetch past chatbot interaction via OpenAI or system context."""
    class Arguments:
        user_id = String(required=True)
    
    response = List(String)
    def mutate(self,info, user_id):
        try:
            result = get_chat_history(user_id)
            return GetChatHistoryMutation(response=result)
        except Exception as ex:
            return GetChatHistoryMutation(response=[])


class Mutation(ObjectType):
    chatbot_mutation = ChatMutation.Field()
    chat_history_mutation = GetChatHistoryMutation.Field()
    clear_chat_history_mutation = ClearChatMutation.Field()

schema = graphene.Schema(mutation=Mutation)
