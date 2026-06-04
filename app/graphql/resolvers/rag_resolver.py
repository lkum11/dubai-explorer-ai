from flask import current_app
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from app.rag.embedder import get_embedding_model
from app.config import ES_INDEX_NAME, TOP_K, GENERATION_MODEL
from app.auth.middleware import require_auth
from app.rag.agentic.graph import run_agentic_rag

import logging

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.85


@require_auth
def resolve_askRAG(root, info, query_text):
    try:
        logger.info(f"askRAG resolver called with query: '{query_text[:60]}'")
        embedder = get_embedding_model()
        client = current_app.openai_client
        es_client = current_app.es_client

        retriever = Retriever(es_client, embedder, index_name=ES_INDEX_NAME, top_k=TOP_K)
        relevant_chunks = retriever.retrieve(query_text=query_text)

        if not relevant_chunks:
            return "I don't have enough information to answer that question."

        # Get top retrieval confidence score
        top_score = relevant_chunks[0]["score"]
        logger.info(f"Top retrieval score: {top_score:.3f} | threshold: {CONFIDENCE_THRESHOLD}")

        if top_score >= CONFIDENCE_THRESHOLD:
            # High confidence → direct generation, no verification needed
            generator = Generator(client=client, model=GENERATION_MODEL)
            return generator.generate(query_text=query_text, retrieved_chunks=relevant_chunks)
        else:
            # Low confidence → agentic verification loop
            result = run_agentic_rag(
                query_text=query_text,
                retrieved_chunks=relevant_chunks,
                client=client,
                model=GENERATION_MODEL
            )
            logger.info(f"Agentic RAG complete — grounded={result['is_grounded']}, retries={result['retry_count']}")
            return result["final_answer"]

    except Exception:
        logger.exception(f"Unexpected exception for query: {query_text[:60]}")
        raise