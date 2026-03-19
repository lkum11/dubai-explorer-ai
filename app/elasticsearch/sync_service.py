from app.db import db
import logging
from app.models import WikiChunk
from flask import current_app
from app.config import ES_INDEX_NAME
from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)

def fetch_unindexed_chunks():
    try:
        unindexed_chunks = db.session.query(WikiChunk).filter_by(is_indexed=False).all()
        logger.info(f"Fetched {len(unindexed_chunks)} unindexed chunks.")

        return unindexed_chunks
    
    except Exception:
        logger.exception(f"failed to fetch unindexed chunks from DB.")
        return []

def prepare_es_document(unindexed_chunks):
    """To prepare ES document for each unindexed chunks"""
    try:
        documents = []
        for chunk in unindexed_chunks:
            doc = {
                "page_id": chunk.article.page_id,
                "_id": chunk.id,
                "title": chunk.article.title,
                "text": chunk.text,
                "chunk_index": chunk.chunk_index,
                "embedding": chunk.embedding, 
                "source": chunk.article.source,
                "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
                "updated_at": chunk.updated_at.isoformat() if chunk.updated_at else None,
            }
            documents.append(doc)
        logger.info(f"Prepared {len(documents)} documents for indexing.")
        return documents
    
    except Exception:
        logger.exception(f"Failed to prepare ES documents.")
        return []
    
def bulk_index_to_elasticsearch(documents):
    """Bulk upload to Elasticsearch"""
    try:
        if not documents:
            logger.info("No valid documents prepared for indexing.")
            return {"success": 0, "errors": 0}
        
        es = current_app.es_client
        actions = []
        for doc in documents:
            # pop removes "_id" from the dict and returns it
            doc_id = doc.pop("_id", None)
            actions.append({
                "_index": ES_INDEX_NAME,
                "_id": doc_id,
                "_source": doc
            })
        # using bulk() helper for simplicity, can be extended with streaming_bulk()
        success_count, errors = bulk(es, actions, raise_on_error=False, stats_only=True)
        
        logger.info(f"Bulk index completed - Success: {success_count}, Errors: {errors}")

        return {"success": success_count, "errors": errors }

    except Exception:
        logger.exception(f"Failed to create index.")
        return {"success": 0, "errors": 0}


def sync_to_elasticsearch():
    """
    Fetch unindexed chunks → prepare documents → bulk upload to Elasticsearch → mark as indexed.
    """
    try:
        chunks = fetch_unindexed_chunks()
        if not chunks:
            logger.info("No unindexed chunks found.")
            return
        docs = prepare_es_document(chunks)
        logger.info(f"Attempting to index {len(docs)} documents to Elasticsearch.")
        result = bulk_index_to_elasticsearch(documents=docs)
        success_count = result["success"]
        errors = result["errors"]

        if errors:
            logger.error(f"Some documents failed to index: {errors}. Not marking chunks yet.")
            return
        
        for chunk in chunks:
            chunk.is_indexed = True

        db.session.commit()
        
        logger.info(f"Synced {success_count} chunks to Elasticsearch.")

    except Exception:
        logger.exception("Failed sync to Elasticsearch.")
        db.session.rollback()
