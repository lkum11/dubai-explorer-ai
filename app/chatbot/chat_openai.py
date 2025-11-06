from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def openai_chat_response(user_input: str) -> str:
    """
    Generates a chatbot response using OpenAI GPT model.
    """
    if not user_input:
        raise ValueError("Empty input provided to chatbot")

    client = OpenAI(
        # api_key=os.getenv("OPENAI_API_KEY"),
        # project=os.getenv("OPENAI_PROJECT")
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=user_input
    )

    print("✅ Response:", response.output_text)
    return response.output_text
