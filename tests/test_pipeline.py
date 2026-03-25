from unittest.mock import patch, MagicMock
from app.rag.pipeline import run_wiki_ingestion_pipeline


@patch("app.rag.pipeline.sync_to_elasticsearch")
@patch("app.rag.pipeline.embed_articles")
@patch("app.rag.pipeline.save_chunks_to_db")
@patch("app.rag.pipeline.chunk_articles")
@patch("app.rag.pipeline.save_articles_to_db")
@patch("app.rag.pipeline.parse_wikipedia_text")
@patch("app.rag.pipeline.fetch_wikipedia_page")
@patch("app.rag.pipeline.db")
class TestRunWikiIngestionPipeline:

    def test_no_articles_parsed_returns_early(
        self, mock_db, mock_fetch, mock_parse,
        mock_save_articles, mock_chunk, mock_save_chunks,
        mock_embed, mock_sync
    ):
        mock_fetch.return_value = {}
        mock_parse.return_value = []

        run_wiki_ingestion_pipeline()

        mock_save_articles.assert_not_called()
        mock_chunk.assert_not_called()
        mock_save_chunks.assert_not_called()
        mock_embed.assert_not_called()
        mock_sync.assert_not_called()

    def test_full_pipeline_calls_all_stages(
        self, mock_db, mock_fetch, mock_parse,
        mock_save_articles, mock_chunk, mock_save_chunks,
        mock_embed, mock_sync
    ):
        mock_fetch.return_value = {}
        mock_parse.return_value = [{"title": "Burj Khalifa", "page_id": 794957}]
        mock_save_articles.return_value = {"inserted": 1, "updated": 0, "failed": 0}
        mock_chunk.return_value = [{"chunk_id": "123", "text": "some text"}]
        mock_db.session.query.return_value.filter_by.return_value.all.return_value = [
            MagicMock(is_chunked=False, page_id=794957, title="Burj Khalifa",
                      summary="The Burj Khalifa...", source="wikipedia")
        ]

        run_wiki_ingestion_pipeline()

        mock_save_articles.assert_called_once()
        mock_chunk.assert_called_once()
        mock_save_chunks.assert_called_once()
        mock_embed.assert_called_once()
        mock_sync.assert_called_once()

    def test_embed_and_sync_always_called_regardless_of_chunking(
        self, mock_db, mock_fetch, mock_parse,
        mock_save_articles, mock_chunk, mock_save_chunks,
        mock_embed, mock_sync
    ):
        mock_fetch.return_value = {}
        mock_parse.return_value = [{"title": "Burj Khalifa", "page_id": 794957}]
        mock_save_articles.return_value = {"inserted": 0, "updated": 1, "failed": 0}
        
        # No unchunked articles — already processed
        mock_db.session.query.return_value.filter_by.return_value.all.return_value = []

        run_wiki_ingestion_pipeline()

        # Chunking skipped — no new articles
        mock_chunk.assert_not_called()
        mock_save_chunks.assert_not_called()

        # But embed and sync ALWAYS run
        mock_embed.assert_called_once()
        mock_sync.assert_called_once()