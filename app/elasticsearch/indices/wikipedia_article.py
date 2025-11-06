# app/elasticsearch/indices/wikipedia_article.py
SETTINGS = {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }

MAPPINGS = {
    "properties": {
        "page_id": {"type": "keyword", "ignore_above": 256},
        "chunk_id": {"type": "keyword", "ignore_above": 256},
        "title": {
            "type": "text",
            "fields": {"raw": {"type": "keyword"}}
        },
        "text": {"type": "text", "index_options": "positions"},
        "chunk_index": {"type": "integer"},
        "embedding": {
            "type": "dense_vector",
            "dims": 1536,
            "index": True,
            "similarity": "cosine"
        },
        "source": {"type": "keyword", "ignore_above": 256},
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"}
    }
}