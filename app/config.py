# app/config.py
import os

# Wikipedia
WIKI_TITLES = [
    "Burj Khalifa",
    "Palm Jumeirah",
]

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Elasticsearch
ES_INDEX_NAME = "wiki_articles_vector"

EMBEDDING_MODEL = "text-embedding-3-small"

TOP_K = 5
NUM_CANDIDATES = 50