import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from flask import current_app


def hash_password(plain_password:str) -> str:
    """Hash a plain password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def generate_token(user_id: int, email: str) -> str:
    """Generate a JWT access token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(
        payload=payload,
        key=current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

def validate_token(token: str) -> dict:
    """Validate a JWT token and return payload."""
    try:
        return jwt.decode(
            jwt=token,
            key=current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
