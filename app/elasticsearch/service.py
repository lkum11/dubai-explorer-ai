from elasticsearch import Elasticsearch, ConnectionError, AuthenticationException
import os
import logging

logger = logging.getLogger(__name__)


def get_es_client():
    try:
        if not os.getenv("ELASTICSEARCH_URL"):
            raise EnvironmentError("ELASTICSEARCH_URL not set in environment.")
        
        es_client = Elasticsearch(
            os.getenv("ELASTICSEARCH_URL"),
            headers={
                "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
                "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
            },
        )

        info = es_client.info()
        logger.info(f"Connected to cluster '{info['cluster_name']}' (v{info['version']['number']})")
        return es_client

    except Exception:
        logger.exception("Failed to initialize ES client.")
