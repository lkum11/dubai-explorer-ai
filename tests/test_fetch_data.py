from app.rag.fetch_data import fetch_wikipedia_page, parse_wikipedia_text
from unittest.mock import patch
import requests as req

class TestFetchWikipediaPage:

    def test_empty_title_returns_400(self):
        result = fetch_wikipedia_page([])
        assert result["status"] == 400
        assert result["data"] is None

    def test_none_titles_returns_400(self):
        result = fetch_wikipedia_page(None)
        assert result["status"] == 400
        assert result["data"] is None

    def test_pagination_merges_articles_correctly(self, wiki_page1, wiki_page2):
        
        with patch(
            "app.rag.fetch_data.requests.get",
            side_effect=[wiki_page1, wiki_page2]
        ):
            result = fetch_wikipedia_page(["Burj Khalifa", "Palm Jumeirah"])

        pages = result["data"]["query"]["pages"]
        assert len(pages["794957"]["extract"]) > 0
        assert len(pages["3162976"]["extract"]) > 0
    
    def test_timeout_returns_408(self):
        
        with patch(
            "app.rag.fetch_data.requests.get",
            side_effect=req.exceptions.Timeout
        ):
            result = fetch_wikipedia_page(["Burj Khalifa"])

        assert result["status"] == 408
        assert result["data"] is None
    
    def test_api_failure_returns_none(self):
        with patch(
            "app.rag.fetch_data.requests.get",
            side_effect=Exception("Network error")
        ):
            result = fetch_wikipedia_page(["Burj Khalifa"])

        assert result["status"] is None
        assert result["data"] is None

    

class TestParseWikipediaText:

    def test_parses_valid_article(self, parsed_page_json):
        result = parse_wikipedia_text(parsed_page_json)

        assert len(result) == 1
        assert result[0]["title"] == "Burj Khalifa"
        assert result[0]["page_id"] == 794957
        assert result[0]["source"] == "wikipedia"
        assert result[0]["word_count"] > 0
        assert result[0]["char_count"] > 0

    def test_skips_article_with_empty_extract(self, empty_extract_page_json):
        result = parse_wikipedia_text(empty_extract_page_json)
        assert len(result) == 0

    def test_missing_pages_returns_empty_list(self, missing_pages_json):
        result = parse_wikipedia_text(missing_pages_json)
        assert result == []
