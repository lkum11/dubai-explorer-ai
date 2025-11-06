from dotenv import load_dotenv
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def get_open_ai_client():
    try:
        client = OpenAI()
        return client
    except Exception:
        logger.exception("Failed to initialize OpenAI client — check API key or environment variables.")
        raise
