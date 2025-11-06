import logging
from app import create_app
from app.elasticsearch.index_manager import ElasticsearchIndexManager
from app.elasticsearch.indices.wikipedia_article import SETTINGS, MAPPINGS
from app.rag.pipeline import run_wiki_ingestion_pipeline

logger = logging.getLogger(__name__)

def main():
    """Initialize database, create Elasticsearch index, and run ingestion pipeline."""
    try:
        app = create_app()
        with app.app_context():
            logger.info("setting up elastic search index...")
            manager = ElasticsearchIndexManager()
            index_name = "wiki_articles_vector"

            if not manager.es.indices.exists(index=index_name):
                manager.create_rag_index(
                    index_name=index_name,
                    settings=SETTINGS,
                    mapping=MAPPINGS
                )
                logger.info(f"Index '{index_name}' created.")
            else:
                logger.info(f"Index '{index_name}' already exists.")
            
            # Run full ingestion pipeline
            logger.info("🚀 Running ingestion + chunk + embed + sync pipeline...")
            run_wiki_ingestion_pipeline()
            logger.info("🎯 Pipeline execution completed successfully.")

    except Exception:
        logger.exception("Error during pipeline initialization.")


if __name__ == "__main__":
    main()