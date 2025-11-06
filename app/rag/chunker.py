from datetime import datetime, timezone
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid


logger = logging.getLogger(__name__)

def chunk_articles(parsed_articles: list[dict]) -> list[dict]:
    """
    Splits Wikipedia article summaries into smaller chunks for embedding.

    Args:
        parsed_articles (list[dict]): Parsed articles containing 'title', 'page_id', and 'summary'.
        chunk_size (int): Max characters per chunk (default=500).
        chunk_overlap (int): Overlap between consecutive chunks (default=50).

    Returns:
        list[dict]: A list of text chunks ready for embedding, with metadata.
    """
    try:
        if not parsed_articles:
            logger.warning("No articles available to chunk.")
            return []
        
        chunks = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
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
