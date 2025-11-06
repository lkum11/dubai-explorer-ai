import os, redis, logging
import time
from flask import Flask, jsonify
from flask_graphql import GraphQLView
from app.db import db
from flask_migrate import Migrate
from app.rag.openai_client import get_open_ai_client
from app.elasticsearch.service import get_es_client

# Always log in UTC for consistent timestamps across environments
logging.Formatter.converter = time.gmtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Initialize Redis
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))


class Config:
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/appdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    # Auto-create tables only in dev 
    if os.getenv("FLASK_ENV") == "development":
        with app.app_context():
            db.create_all()
            logger.info("Database tables auto-created (development mode).")
    
    app.redis = redis_client
    try:
        app.es_client = get_es_client()
        logger.info("Elasticsearch client initialized successfully.")

    except Exception:
        app.es_client = None
        logger.exception("Failed to initialize Elasticsearch client at startup.")

    try:
        app.openai_client = get_open_ai_client()
        logger.info("OpenAI client initialized successfully.")

    except Exception:
        app.openai_client = None
        logger.exception("Failed to initialize OpenAI client at startup.")
        
    logger.info("Flask app setup complete. Ready to accept requests.")

    from app.graphql.schema import schema
    
    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True),
    )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    # Redis test route
    @app.get("/ping_redis")
    def ping_redis():
        try:
            pong = app.redis.ping()
            return jsonify(redis="connected", pong=pong)
        except Exception as e:
            return jsonify(redis="error", error=str(e)), 500
        
    from app.tasks import add_numbers, send_welcome_email

    @app.get("/run_task")
    def run_task():
        result = add_numbers.delay(10, 5)
        return jsonify(
            message="Task submitted",
            task_id=result.id
        )
    
    @app.get("/send_email")
    def trigger_email():
        task = send_welcome_email.delay("joinlovely@gmail.com", "Lovely")
        return jsonify(message="Email task queued", task_id=task.id)
    
    logger.info("Flask app initialized with Redis and GraphQL")

    return app
