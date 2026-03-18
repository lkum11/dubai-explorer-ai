from datetime import datetime, timezone
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
import uuid


logger = logging.getLogger(__name__)

def chunk_articles(parsed_articles: list[dict]) -> list[dict]:
    """
    Args:
        parsed_articles (list[dict]): Parsed articles containing 'title', 'page_id', and 'summary'.

    Chunking config:
        chunk_size: 800 chars per chunk
        chunk_overlap: 100 chars overlap between consecutive chunks
    """
    try:
        if not parsed_articles:
            logger.warning("No articles available to chunk.")
            return []
        
        chunks = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        for article in parsed_articles:
            texts = text_splitter.split_text(article.get("summary", ""))
            try:
                for index, text in enumerate(texts, start=1):
                    record = {
                        "chunk_id": uuid.uuid4(),
                        "page_id": article.get("page_id"),
                        "title": article.get("title"),
                        "text": text.strip(),
                        "chunk_index": index,
                        "source": article.get("source"),
                        "timestamp": datetime.now(timezone.utc)
                    }
                    chunks.append(record)
            except Exception:
                logger.exception(f"Failed to creare chunk for article:{article.get('title')}")
                continue

        logger.info(
            f"Chunking complete — {len(chunks)} chunks generated from {len(parsed_articles)} articles."
        )
        return chunks
    
    except Exception:
        logger.exception(f"Failed to create chunks for {parsed_articles}")
        return []
