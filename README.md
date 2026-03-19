# Dubai Explorer AI 🏙️
> A production-grade RAG (Retrieval-Augmented Generation) backend system for Dubai travel Q&A — built with Flask, GraphQL, Elasticsearch, and OpenAI.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.14-005571?logo=elasticsearch)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)


## 📌 Overview

Dubai Explorer AI is a **personal backend POC** that demonstrates a complete, production-style RAG system.

It answers natural language questions about Dubai attractions by:
1. Fetching and indexing Wikipedia articles into Elasticsearch as vector embeddings
2. Retrieving semantically relevant chunks at query time using KNN search
3. Generating grounded answers using OpenAI GPT-4o-mini — based **only** on retrieved context

This project was built to demonstrate hands-on expertise in **AI-integrated backend engineering**, distributed systems, and modern Python architecture.

```mermaid
flowchart LR
    User(["👤 User"])

    User -->|"GraphQL query"| Flask

    subgraph Flask ["🌐 Flask + GraphQL"]
        askRAG["askRAG resolver"]
    end

    Flask --> Retriever
    Flask --> Generator

    subgraph RAG ["🧠 RAG"]
        Retriever["Retriever\nKNN search"] -->|"top chunks"| Generator["Generator\nGPT-4o-mini"]
    end

    Retriever --> ES[("Elasticsearch\nvectors")]
    Retriever --> OpenAI["OpenAI\nEmbeddings"]
    Generator --> OpenAI

    Generator -->|"answer"| User

    subgraph Ingestion ["⚙️ Ingestion pipeline"]
        direction LR
        Wikipedia --> Chunker --> PostgreSQL[("PostgreSQL")]
        Chunker --> OpenAI
        OpenAI --> ES
    end

    subgraph Infra ["🔧 Infrastructure"]
        direction LR
        Redis --> Celery["Celery Worker"]
        Kibana["Kibana"]
    end
```