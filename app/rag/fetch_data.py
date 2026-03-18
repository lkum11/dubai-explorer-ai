import requests
import logging

logger = logging.getLogger(__name__)


WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

def fetch_wikipedia_page(titles: list[str]) -> dict:
    """Fetches Wikipedia page content (HTML + metadata) for a given title."""
    try:
        if not titles: # not titles covers both None and empty list cases.
            logger.warning("Invalid title provided")
            return {"status": 400, "data": None}
        
        # Stores best version of each article across all pagination rounds
        all_pages = {}

        params = {
            "action": "query",
            "format": "json",
            "titles": "|".join(list(set([t.strip().title() for t in titles if t.strip()]))),
            "explaintext": 1, # → return plain text, not HTML
            "prop": "extracts", # → return article content
        }
        headers = {
            "User-Agent": "DubaiTourismRAG/0.1 (joinlovely@gmail.com)"
        }
        # timeout=(3, 10): up to 3 seconds to establish a connection and up to 10 seconds for the server to send data

        page_num = 1
        # Wikipedia API pagination explanation:
        # When fetching multiple large articles, Wikipedia returns ONE full extract per request.
        # Remaining articles come back with empty extracts and a 'continue' token.
        # We loop using the continue token until batchcomplete=True.
        # Smart merge: for each article, we keep whichever version has the most content.
        # Example with ["Burj Khalifa", "Palm Jumeirah"]:
        #   Page 1 → Burj Khalifa (29780 chars) + Palm Jumeirah (0 chars) → save both
        #   Page 2 → Burj Khalifa (0 chars) + Palm Jumeirah (7713 chars) → only update Palm Jumeirah
        #   Result → both articles fully fetched 
        while True:
            response = requests.get(WIKI_API_URL, params=params, headers=headers, timeout=(3, 10))

            if not response.ok:
                logger.error(f"Request failed with status={response.status_code}")
                break

            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for key, page in pages.items():
                if key not in all_pages or len(page.get("extract", "")) > len(all_pages[key].get("extract", "")):
                    all_pages[key] = page

            logger.info(f"Fetching page {page_num} for titles: {titles}")
            logger.info(f"Page {page_num}: fetched {len(pages)} articles")
            if "continue" in data:
                logger.info("More pages available, continuing...")

            if "continue" not in data:
                break

            params.update(data["continue"])
            page_num += 1

        logger.info(f"Total pages fetched: {len(all_pages)}")
        return {
            "status": 200,
            "data": {"query": {"pages": all_pages}}
        }
    
    except requests.exceptions.Timeout:
        logger.exception("Wikipedia API request timed out. Try again later.")
        return {"status": 408, "data": None}
    
    except Exception:
        logger.exception(f"Unexpected exception while fetching details for {titles}")
        return {"status": None, "data": None}


def parse_wikipedia_text(page_json: dict) -> list[dict]:
    """Extracts clean plain text from the Wikipedia page JSON."""
    try:
        pages = page_json["data"].get("query", {}).get("pages", {})
        if not pages:
            logger.error(f"Empty or missing page data")
            return []
        
        result = []
        for key, value in pages.items():
            extract = value.get("extract") or ""
            if not extract:
                continue
            result.append({
                "page_id": int(value.get("pageid", key)),
                "title": value.get("title","").strip(),
                "summary": extract.strip(),
                "word_count": len((extract).split()),
                "char_count": len(extract),
                "source": "wikipedia"
            })
                
        return result

    except Exception:
        logger.exception(f"Unexpected exception while parsing data")
        return []

