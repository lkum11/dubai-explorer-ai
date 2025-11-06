import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
# from flask import current_app
from app import redis_client

load_dotenv()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
    You are a helpful travel assistant for Pelago by Singapore Airlines. Always answer in a friendly, concise tone.
"""

def chat_system_response(user_input: str, user_id: str) -> str:
    """
    Generates a chatbot response using OpenAI GPT model.
    """
    if not user_input or not user_input.strip():
        raise ValueError("Empty input provided to chatbot")
    # redis_client = current_app.redis
    key = f"chat_history:{user_id}"
    # TODO: Replace direct import with `current_app.redis` once app context refactor is complete.
    data = redis_client.get(key)
    
    if data:
        message_history = json.loads(data)
    else:
        message_history = [{ "role": "system", "content": SYSTEM_PROMPT }]

    message_history.append({"role": "user", "content": user_input})

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        input=message_history
    )
    message_history.append({"role": "assistant", "content": response.output_text})
    redis_client.set(key, json.dumps(message_history))
    redis_client.expire(key, 3600)  # optional TTL 1 hour

    logging.info("✅ Response:", response.output_text)
    return response.output_text
