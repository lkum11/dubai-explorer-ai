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

## 🏗️ Architecture
```mermaid
flowchart TD
    User(["👤 User"])
    GQL["Flask + GraphQL API\naskRAG resolver"]
    RET["Retriever\nKNN vector search"]
    GEN["Generator\nGPT-4o-mini"]
    ES[("Elasticsearch\nVector index 1536d")]
    OAI["OpenAI API\nEmbeddings + Chat"]
    PG[("PostgreSQL\nSource of truth")]

    User -->|GraphQL query| GQL
    GQL --> RET
    GQL --> GEN
    RET -->|embed query| OAI
    RET -->|KNN search| ES
    RET -->|top chunks| GEN
    GEN -->|generate answer| OAI
    GEN -->|answer| User

    subgraph Ingestion ["⚙️ Ingestion Pipeline (run once)"]
        WIKI["Wikipedia API"] -->|fetch| CHUNK["Chunker\n1000 chars"]
        CHUNK -->|save| PG
        CHUNK -->|embed| OAI
        OAI -->|vectors| ES
    end

    subgraph Supporting ["🔧 Supporting Services"]
        REDIS["Redis\nTask broker"]
        CELERY["Celery Worker\nAsync tasks"]
        BEAT["Celery Beat\nScheduled tasks"]
        KIBANA["Kibana\nES monitoring"]
        REDIS --> CELERY
        REDIS --> BEAT
    end
```