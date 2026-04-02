from functools import wraps
from flask import request
from app.auth.utils import validate_token
import logging

logger = logging.getLogger(__name__)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            raise Exception("Authentication required — token is missing")
        
        try:
            payload = validate_token(token=token)
            request.current_user = payload
            logger.info(f"Authenticated user: {payload.get('email')}")

        except ValueError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise Exception(str(e))
        
        return f(*args, **kwargs)
    
    return decorated