from app.db import db
import uuid
from datetime import datetime, timezone


class User(db.Model):
    __tablename__ = "users"
    # TODO: make id column uuid later
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"


class WikiArticle(db.Model):
    __tablename__ = "wikiarticle"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), unique=True, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    char_count = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(150), nullable=False)
    is_chunked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    # Relationship to WikiChunk
    chunks = db.relationship(
        "WikiChunk",
        back_populates="article",
        # To Ensures chunks are automatically deleted when an article is removed
        cascade="all, delete-orphan" 
    )

    def __repr__(self):
        return f"<WikiArticle {self.title}>"


class WikiChunk(db.Model):
    __tablename__ = "wikichunk"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = db.Column(
        db.String(36),
        db.ForeignKey("wikiarticle.id", ondelete="CASCADE"),
        nullable=False
    )
    chunk_index = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.JSON, nullable=True)
    is_embedded = db.Column(db.Boolean, default=False)
    is_indexed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    # Back reference to WikiArticle
    article = db.relationship("WikiArticle", back_populates="chunks")
    
    def __repr__(self):
        return f"<WikiChunk {self.chunk_index} of {self.article_id}>"