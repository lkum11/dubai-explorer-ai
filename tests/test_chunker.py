from app.rag.chunker import chunk_articles

class TestChunkArticles:

    def test_empty_articles_returns_empty_list(self):
        result = chunk_articles([])
        assert result == []

    def test_valid_article_returns_chunks(self, parsed_articles):
        result = chunk_articles(parsed_articles)
        assert len(result) > 0

    def test_chunk_has_required_fields(self, parsed_articles):
        result = chunk_articles(parsed_articles)
        chunk = result[0]
        assert "chunk_id" in chunk
        assert "page_id" in chunk
        assert "title" in chunk
        assert "text" in chunk
        assert "chunk_index" in chunk
        assert "source" in chunk
        assert "timestamp" in chunk

    def test_chunk_index_starts_at_one(self, parsed_articles):
        result = chunk_articles(parsed_articles)
        assert result[0]["chunk_index"] == 1

    def test_chunk_metadata_matches_article(self, parsed_articles):
        result = chunk_articles(parsed_articles)
        assert result[0]["page_id"] == 794957
        assert result[0]["title"] == "Burj Khalifa"
        assert result[0]["source"] == "wikipedia"

    def test_long_article_produces_multiple_chunks(self, parsed_articles):
        result = chunk_articles(parsed_articles)
        assert len(result) > 1