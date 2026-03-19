from app.models import User
import logging

logger = logging.getLogger(__name__)

def resolve_users(root, info):
    try:
        return User.query.all()
    except Exception:
        logger.exception("Failed to fetch users")
        return []

def resolve_user(root, info, id):
    try:
        return User.query.get(id)
    except Exception:
        logger.exception(f"Failed to fetch user id={id}")
        return None