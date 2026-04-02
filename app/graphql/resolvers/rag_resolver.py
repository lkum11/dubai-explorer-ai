from flask import current_app
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from app.rag.embedder import get_embedding_model
from app.config import ES_INDEX_NAME, TOP_K, GENERATION_MODEL
from app.auth.middleware import require_auth
import logging

logger = logging.getLogger(__name__)

@require_auth
def resolve_askRAG(root, info, query_text):
    try:
        logger.info(f"askRAG resolver called with query: '{query_text[:60]}'")
        embedder = get_embedding_model()
        client = current_app.openai_client
        es_client = current_app.es_client

        retriever = Retriever(es_client, embedder, index_name=ES_INDEX_NAME, top_k=TOP_K)
        relevant_chunks = retriever.retrieve(query_text=query_text)

        generator = Generator(client=client, model=GENERATION_MODEL)
        return generator.generate(query_text=query_text, retrieved_chunks=relevant_chunks)

    except Exception:
        logger.exception(f"Unexpected exception for query: {query_text[:60]}")
        raise