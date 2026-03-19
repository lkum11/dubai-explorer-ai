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
flowchart TB
    User(["👤 User"])

    subgraph API ["🌐 API Layer"]
        GQL["Flask + GraphQL\naskRAG resolver"]
    end

    subgraph RAG ["🧠 RAG Pipeline"]
        RET["Retriever\nKNN vector search"]
        GEN["Generator\nGPT-4o-mini"]
    end

    subgraph Storage ["🗄️ Storage"]
        ES[("Elasticsearch\nvector index")]
        PG[("PostgreSQL\nsource of truth")]
        OAI["OpenAI API"]
    end

    subgraph Ingestion ["⚙️ Ingestion (run once)"]
        WIKI["Wikipedia"] --> CHUNK["Chunker"]
        CHUNK --> PG
        CHUNK --> OAI
        OAI --> ES
    end

    subgraph Supporting ["🔧 Supporting"]
        REDIS["Redis"] --> CELERY["Celery Worker"]
        REDIS --> BEAT["Celery Beat"]
        KIBANA["Kibana"]
    end

    User -->|query| GQL
    GQL --> RET & GEN
    RET --> OAI & ES
    RET -->|chunks| GEN
    GEN -->|answer| User
```