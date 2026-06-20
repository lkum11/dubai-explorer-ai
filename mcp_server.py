import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env FIRST — before any app imports
env_path = Path(__file__).parent / ".env"
loaded = load_dotenv(dotenv_path=env_path)

# NOW import app modules (key is available)
import logging
from fastmcp import FastMCP
from elasticsearch import Elasticsearch
from app.rag.retriever import Retriever
from app.rag.embedder import get_embedding_model
from app.config import ES_INDEX_NAME, TOP_K

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f".env loaded: {loaded}, key present: {bool(os.getenv('OPENAI_API_KEY'))}")

# Standalone clients (no Flask dependency) 
es_url = os.getenv("ELASTICSEARCH_URL_LOCAL", "http://localhost:9200")
es_client = Elasticsearch(es_url)
logger.info(f"MCP server connecting to ES at: {es_url}")

embedder = get_embedding_model()

# MCP Server
mcp = FastMCP("Dubai Explorer AI")

@mcp.tool
def search_places(query: str, k:int = TOP_K) -> list[dict]:
    """
    Search Dubai attractions and places using semantic vector search.

    Args:
        query: Natural language search query (e.g. "attractions at Palm Jumeirah")
        k: Number of results to return (default 5)

    Returns:
        List of relevant chunks with title, text, page_id, and relevance score.
    """
    logger.info(f"search_places called: query='{query}', k={k}")
    retriever = Retriever(
        es_client=es_client,
        embedder=embedder,
        index_name=ES_INDEX_NAME,
        top_k=k
    )
    results = retriever.retrieve(query_text=query)
    logger.info(f"search_places returning {len(results)} results")
    return results


if __name__ == "__main__":
    mcp.run()  # STDIO transport by default