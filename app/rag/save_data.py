from app.db import db
from app.models import WikiArticle, WikiChunk
import logging

logger = logging.getLogger(__name__)


def update_record(record, article):
    try:
        record.page_id = article.get("page_id")
        record.title = article.get("title")
        record.summary = article.get("summary")
        record.word_count = article.get("word_count")
        record.char_count = article.get("char_count")
        record.source = "Wikipedia"
        return record
    except Exception:
        logger.exception(f"Unexpected while updating record for article: {article} with record:{record}")


def save_articles_to_db(parsed_articles: list[dict]) -> dict:
    """
    Saves or updates parsed Wikipedia articles into the database.
    Returns a summary of inserted, updated, and failed counts.

    input data :
            [
                {
                    "page_id": 35946091,
                    "title": "Burj Khalifa",
                    "summary": "The Burj Khalifa is a skyscraper in Dubai...",
                    "word_count": 87,
                    "char_count": 512
                },
                {
                    "page_id": 3162976,
                    "title": "Palm Jumeirah",
                    "summary": "The Palm Jumeirah is an artificial archipelago...",
                    "word_count": 102,
                    "char_count": 620
                }
            ]
    output_data:
        {
            "inserted": 2,
            "updated": 0,
            "failed": 0
        }
        or (if article already present)
        {
            "inserted": 1,
            "updated": 1,
            "failed": 0
        }
    """
    try:
        if not parsed_articles:
            logger.info(f"No record available to save.")
            return {"inserted": 0, "updated": 0, "failed": 0}
        
        inserted = 0
        updated = 0
        for article in parsed_articles:
            record = db.session.query(WikiArticle).filter_by(
                page_id=article.get("page_id")
            ).first()

            if not record:
                record = WikiArticle()
                update_record(record, article)
                inserted += 1
            else:
                update_record(record, article)
                updated += 1

            db.session.add(record)
        db.session.commit()
        logger.info(f"Articles saved — inserted={inserted}, updated={updated}")

        return {
            "inserted": inserted,
            "updated": updated,
            "failed": 0
        }
    except Exception:
        db.session.rollback()
        logger.exception(f"Unexpected exception while saving articles to database")
        return {
            "inserted": 0,
            "updated": 0,
            "failed": len(parsed_articles)
        }


def save_chunks_to_db(chunks: list[dict]) -> dict:
    """
        Saves article chunks into the database.
        Returns a summary of inserted and failed counts.
    """
    try:
        if not chunks:
            logger.info(f"no record available to save")
            return {"inserted": 0, "failed": 0}
        
        inserted = 0
        failed = 0

        logger.info(f"Preparing to save {len(chunks)} chunks.")
        
        for chunk in chunks:
            article = db.session.query(WikiArticle.id).filter_by(
                page_id=chunk.get("page_id","")
            ).first()
            
            if not article:
                logger.error(f"Skipping chunk: No article found for page_id={chunk.get('page_id','')}")
                failed += 1
                continue

            record = WikiChunk()
            record.text =  chunk.get("text")
            record.chunk_index = chunk.get("chunk_index")
            record.article_id = article.id
            record.is_embedded = False
            db.session.add(record)
            inserted += 1

        db.session.commit()
        logger.info(f"Saved {inserted} chunks to DB.")

        return {"inserted": inserted, "failed": failed}
    
    except Exception:
        db.session.rollback()
        logger.exception(f"Unexpected exception while saving chunks to database")
        return {
            "inserted": 0,
            "failed": len(chunks)
        }