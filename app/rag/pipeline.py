from app.db import db
import logging
from app.models import WikiArticle
from app.rag.fetch_data import parse_wikipedia_text, fetch_wikipedia_page
from app.rag.save_data import save_articles_to_db, save_chunks_to_db
from app.rag.chunker import chunk_articles
from app.rag.embedder import embed_articles
from app.elasticsearch.sync_service import sync_to_elasticsearch
from app.config import WIKI_TITLES

logger = logging.getLogger(__name__)

def run_wiki_ingestion_pipeline():
    """Ingestion pipeline for RAG — fetch, chunk, embed and sync to Elasticsearch."""
    try:
        logger.info("Starting ingestion pipeline...")

        # ── Stage 1: Fetch & Parse ──────────────────────────
        page_json = fetch_wikipedia_page(WIKI_TITLES)
        parsed_articles = parse_wikipedia_text(page_json=page_json)
        if not parsed_articles:
            logger.info("No articles parsed.")
            return
        
        # ── Stage 2: Save to PostgreSQL ─────────────────────
        response = save_articles_to_db(parsed_articles=parsed_articles)
        logger.info(f"Summary of saved articles : {response}")
        
        # ── Stage 3: Chunk ──────────────────────────────────
        unchunked_articles = db.session.query(WikiArticle).filter_by(
            is_chunked=False
        ).all()

        if not unchunked_articles:
            logger.info("No new articles to chunk.")
        else:
        
            # Chunk and Save to DB
            parsed_dicts = [
                {
                    "page_id": a.page_id,
                    "title": a.title,
                    "summary": a.summary,
                    "source": a.source
                }
                for a in unchunked_articles
            ]
            
            chunks = chunk_articles(parsed_dicts)
            save_chunks_to_db(chunks)

            # Mark articles as chunked in wikiarticle table
            for article in unchunked_articles:
                article.is_chunked = True
            db.session.commit()

            logger.info("Ingestion + Chunking pipeline completed.")

        # ── Stage 4: Embed ──────────────────────────────────
        logger.info("Embedding unprocessed chunks...")
        embed_articles()
        logger.info("Embedding complete.")

        # ── Stage 5: Sync to Elasticsearch ──────────────────
        logger.info("Syncing to Elasticsearch...")
        sync_to_elasticsearch()
        logger.info("Indexing complete.")


        logger.info("Full RAG ingestion pipeline complete")
    except Exception:
        logger.exception("Unexpected exception while running RAG ingestion pipeline ")

