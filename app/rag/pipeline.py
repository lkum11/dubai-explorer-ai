from app.db import db
import logging
from app.models import WikiArticle
from app.rag.fetch_data import parse_wikipedia_text, fetch_wikipedia_page
from app.rag.save_data import save_articles_to_db, save_chunks_to_db
from app.rag.chunker import chunk_articles
from app.rag.embedder import embed_articles
from app.elasticsearch.sync_service import sync_to_elasticsearch

logger = logging.getLogger(__name__)

def run_wiki_ingestion_pipeline():
    """Ingetion pipeline for RAG"""
    try:
        logger.info("Starting ingestion pipeline...")

        # Fetch and Parse
        page_json = fetch_wikipedia_page(["Burj Khalifa", "Palm Jumeirah"]) # Note: Only able to fetch one title at a time
        parsed_articles = parse_wikipedia_text(page_json=page_json)
        if not parsed_articles:
            logger.info("No articles parsed.")
            return
        else:
            # Save articles to DB
            response = save_articles_to_db(parsed_articles=parsed_articles)
            logger.info(f"Summary of saved articles : {response}")
        
        # Chunking Stage
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

        # Embedding Stage
        logger.info("Embedding unprocessed chunks...")
        embed_articles()
        logger.info("Embedding complete.")

        # Sync-to-Elastic Stage
        logger.info("Syncing to Elasticsearch...")
        sync_to_elasticsearch()
        logger.info("Indexing complete.")


        logger.info("Full RAG ingestion pipeline complete")
    except Exception:
        logger.exception("Unexpected exception while running RAG ingestion pipeline ")

