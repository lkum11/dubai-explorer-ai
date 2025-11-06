import json
from app import redis_client
import logging

logger = logging.getLogger(__name__)

def get_chat_history(user_id: str) -> list:
    """Fetch user's chat history from Redis. Returns [] if not found or Redis is down."""
    try:
        if not user_id or not user_id.strip():
            logger.warning("Invalid user_id provided")
            return []
        
        key = f"chat_history:{user_id}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return []
    except Exception:
        logger.exception(f"Unexpected behaviour while fetching chat history for user: {user_id}")
        return []


def clear_chat_history(user_id: str) -> bool:
    """Delete user's chat history from Redis. Returns True if deleted, False otherwise."""
    try:
        if not user_id or not user_id.strip():
            logger.warning("Invalid user_id provided")
            return False
        
        key = f"chat_history:{user_id}"
        deletion_count = redis_client.delete(key) # Redis .delete() returns the number of keys removed (0 or 1).
        if deletion_count == 1:
            logger.info(f"chat history deleted successfully for user: {user_id}")
            return True
        return False
    except Exception:
        logger.exception(f"Unexpected behaviour while deleting chat history for user: {user_id}")
        return False
