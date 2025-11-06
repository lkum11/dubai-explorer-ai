from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
import logging
from app.db import db
from app.models import WikiChunk

logger = logging.getLogger(__name__)


client = OpenAI()
# Vector Embeddings
# Elasticsearch mapping expects 1536 dimensions hence used text-embedding-3-small.
# TODO : move "text-embedding-3-small" to env 
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
# get_embedding
def get_embedding_model() -> OpenAIEmbeddings:
    """To get open ai embedding model."""
    return embedding_model

def embed_articles(chunks_to_embed=None) -> list[dict]:
    """To create embedding for each chunk and updating wikichunk table"""
    try:
        if not chunks_to_embed:
            chunks_to_embed = db.session.query(WikiChunk).filter_by(is_embedded=False).all()

        if not chunks_to_embed:
            logger.info("No chunks available for embedding.")
            return []

        failed = 0
        processed = 0

        list_of_texts = [
            chunk.text
            for chunk in chunks_to_embed
        ]
        embeddings = embedding_model.embed_documents(list_of_texts)

        for chunk, embedding in zip(chunks_to_embed, embeddings):
            if not embedding:
                failed += 1
                logger.warning(f"Skipped chunk {chunk.id} - embedding returned empty.")

            chunk.embedding = embedding
            chunk.is_embedded = True
            processed += 1
            db.session.add(chunk)

        db.session.commit()

        logger.info({"Embedding complete — processed": processed, "failed": failed, "model": "text-embedding-3-small"})
        return {"processed": processed, "failed": failed, "model": "text-embedding-3-small"}

    except Exception:
        logger.exception(f"Exception while embedding.")
        db.session.rollback()
        return {"processed": 0, "failed": len(chunks_to_embed), "model": "text-embedding-3-small"}