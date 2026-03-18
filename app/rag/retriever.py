from app.config import ES_INDEX_NAME, TOP_K, NUM_CANDIDATES
import logging

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(
        self, es_client, embedder, index_name=ES_INDEX_NAME, top_k=TOP_K
    ):
        self.es_client = es_client
        self.embedder = embedder
        self.index_name = index_name
        self.top_k = top_k

        # ✅ Fail fast if embedder is missing
        assert self.embedder is not None, "Retriever requires a valid embedder instance."
    
    def _embed_query(self, query_text):
        """Convert query text into embedding vector using embedder."""
        try:
            embedding_vector = self.embedder.embed_query(query_text)
            return embedding_vector
        except Exception:
            logger.exception(f"Embedding generation failed for query: {query_text}")
            return None
    
    def _search_es(self,embedding_vector):
        try:
            if not embedding_vector:
                logger.warning("Empty embedding vector — skipping search.")
                return {"hits": {"hits": []}}

            # perform vector search
            response = self.es_client.search(
                index = self.index_name,
                size=self.top_k,
                query={
                    "knn": {
                        "field": "embedding",
                        "query_vector": embedding_vector,
                        # num_candidates: pool size ES considers before returning top_k results
                        # higher = better recall, lower = faster. Rule of thumb: 10x top_k
                        "num_candidates": NUM_CANDIDATES
                    }
                },
                _source=["title", "text", "page_id"]
            )
            return response
        except Exception:
            logger.exception(f"Elasticsearch search failed [index={self.index_name}, top_k={self.top_k}]")
            return {"hits": {"hits": []}}

    def retrieve(self, query_text):
        try:
            logger.info(f"Retrieving top-{self.top_k} documents for query: '{query_text[:60]}'")
            # TODO: Add Redis query cache to avoid redundant OpenAI embedding calls
            embedding_vector = self._embed_query(query_text)
            response = self._search_es(embedding_vector=embedding_vector)

            result = []
            for hit in response["hits"]["hits"]:
                logger.info(f"Score: {hit['_score']} | Title: {hit['_source']['title']}")
                result.append({
                    "title": hit["_source"]["title"],
                    "text": hit["_source"]["text"],
                    "page_id": hit["_source"]["page_id"],
                    "score": hit["_score"]
                })
            if not result:
                logger.warning(f"No results found for query: '{query_text}'")
            return result
        except Exception:
            logger.exception(f"Retriever failed for query: {query_text}")
            return []
