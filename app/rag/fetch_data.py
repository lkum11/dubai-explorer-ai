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
        
        # titles = ["Burj Khalifa", "Palm Jumeirah", "Dubai Mall"] - > "Burj Khalifa|Palm Jumeirah|Dubai Mall"
        # Wikipedia’s API interprets that as: -> Fetch pages whose titles are “Burj Khalifa”, “Palm Jumeirah”, and “Dubai Mall”.
        params = {
            "action": "query",
            "format": "json",
            "titles": "|".join(list(set([t.strip().title() for t in titles if t.strip()]))),
            "explaintext": 1,
            "prop": "extracts",
        }
        headers = {
            "User-Agent": "DubaiTourismRAG/0.1 (lovely@example.com)"
        }
        # timeout=(3, 10): up to 3 seconds to establish a connection and up to 10 seconds for the server to send data

        response = requests.get(WIKI_API_URL, params=params, headers=headers, timeout=(3, 10))

        if response.ok: # response.status_code == 200 vs response.ok : Covers 2xx range
            data = response.json()
            logger.info(f"Fetched data from {response.url} (status={response.status_code})")
        else:
            data=None
            logger.error(f"Request failed with status={response.status_code} for titles={titles}")
        
        if not data.get("query", {}).get("pages"):
            logger.warning(f"No pages found for {titles}")

        return {"status": response.status_code, "data": data}
    
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

