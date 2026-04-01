import logging
from app.db import db
from flask import Blueprint, request, jsonify
from app.models import User
from app.auth.utils import hash_password, verify_password, generate_token


logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.post("/register")
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "username, email and password are required"}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409
        
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    
    except Exception:
        db.session.rollback()
        logger.exception("Error during registration")
        return jsonify({"error": "Internal server error"}), 500
    
    
@auth_bp.post("/login")
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({ "error": "email and password are required"}), 400
        
        user = User.query.filter_by(email=email).first()

        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401
        
        token = generate_token(
            user_id=user.id,
            email=email
        )
        logger.info(f"User logged in: {email}")

        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }), 200
    except Exception:
        logger.exception("Error during login")
        return jsonify({"error": "Internal server error"}), 500
