# Dubai Explorer AI – RAG Backend (Flask + GraphQL + OpenAI + Elasticsearch)

This project is a **production-grade proof of concept (POC)** showcasing a Retrieval-Augmented Generation (RAG) pipeline built with Flask, GraphQL, and OpenAI’s API. It demonstrates how to integrate a modern Python backend with Elasticsearch, Celery, and PostgreSQL to serve AI-powered contextual responses — using Dubai’s attractions and Wikipedia data as sample content.

---

### 🚀 Project Highlights
- Implements a **complete RAG pipeline**: fetch → chunk → embed → index → retrieve → generate.
- **GraphQL API** for querying AI-generated answers (`askRAG` resolver).
- Uses **OpenAI GPT-4o-mini** for generation and **text-embedding-3-small** for embeddings.
- **Elasticsearch vector search** for context retrieval and ranking.
- **Celery + Redis** integrated for background tasks and async workflows.
- Fully **Dockerized** with PostgreSQL, Redis, Elasticsearch, and Flask in isolated services.
- Designed for **clean architecture** and modular expansion (chatbot, tasks, etc.).

---

### 🧠 Tech Stack
**Backend:** Flask, GraphQL, SQLAlchemy, Flask-Migrate  
**Async Tasks:** Celery, Redis  
**Database:** PostgreSQL  
**Search & RAG:** Elasticsearch, OpenAI (GPT-4o-mini, text-embedding-3-small)  
**Containerization:** Docker, Docker Compose  
**Logging & Monitoring:** Python `logging` with structured, UTC-based logs  

---

### ⚙️ Local Setup

#### 1. Clone the repository
```bash
git clone https://github.com/lkum11/dubai-explorer-ai
cd dubai-explorer-ai
```

#### 2. Create a virtual environment (for local run)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configure environment variables
Copy `.env.example` and update credentials:
```bash
cp .env.example .env
```

#### 4. Run using Docker Compose
```bash
docker compose up --build
```

This will start:
- Flask API (GraphQL endpoint)
- PostgreSQL database
- Redis (for Celery)
- Elasticsearch (for vector search)

---

### 🔁 Re-run Ingestion Pipeline

To reinitialize and sync Wikipedia data into Elasticsearch:
```bash
docker compose exec web python -m scripts.init_pipeline
```

This runs:
- Data fetch from Wikipedia  
- Chunking, embedding, and Elasticsearch sync  

---

### 🧩 GraphQL Endpoint
Access the interactive GraphiQL UI at:
```
http://localhost:5000/graphql
```

Example query:
```graphql
{
  askRAG(queryText: "What are the attractions at Palm Jumeirah?")
}
```

---

### 🧰 Optional Features
- **Celery Tasks:** Async background processing (`/run_task`, `/send_email`)
- **Chatbot Module:** (under `app/chatbot/`) – prototype for contextual session-based chat using Redis memory.

---

### 👩‍💻 For Recruiters & Reviewers
This project reflects a **hands-on backend implementation of a modern RAG system**, integrating:
- clean architecture,
- Dockerized services,
- real-world data processing, and
- production-style observability.

It’s designed as a **personal POC** to demonstrate applied expertise in Flask, GraphQL, Elasticsearch, and Generative AI pipelines.

---

**Author:** Lovely Kumari  
**Location:** Dubai, UAE  
**LinkedIn:** [linkedin.com/in/lovely-kumari-1855ba4b](https://www.linkedin.com/in/lovely-kumari-1855ba4b/)
