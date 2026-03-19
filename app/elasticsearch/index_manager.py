from flask import current_app
import logging

logger = logging.getLogger(__name__)


class ElasticsearchIndexManager:
    def __init__(self):
        self.es = current_app.es_client

    def create_rag_index(self, index_name, settings, mapping):
        """ Creates an Elasticsearch index if it doesn't exist."""
        try:
            if self.es.indices.exists(index=index_name):
                logger.info(f"index {index_name} already exists — skipping creation.")
                return
            
            body = {
                "settings": settings,
                "mappings": mapping
            }

            self.es.indices.create(index=index_name, body=body)
            logger.info(f"Created index: {index_name} successfully")

        except Exception as e:
            logger.exception(f"Exception while creating index: {index_name}")
    
    def delete_index(self, index_name):
        """ Deletes an index if it exists."""
        try:
            if self.es.indices.exists(index=index_name):
                self.es.indices.delete(index=index_name)
                logger.info(f"index: {index_name} delete successfully")

            else:
                logger.info(f"index: {index_name} does not exists")

        except Exception:
            logger.exception(f"Exception while deleting index :{index_name}")
    
    def get_index_info(self, index_name):
        """
        Fetch and print detailed index information.
        """
        try:
            if self.es.indices.exists(index=index_name):
                info = self.es.indices.get(index=index_name)
                logger.info(f"Index info for {index_name}: \n{info}")
            else:
                logger.info(f"index:{index_name} does not exists")

        except Exception as e:
            logger.exception(f"Exception while fetching index info for index: {index_name}")
