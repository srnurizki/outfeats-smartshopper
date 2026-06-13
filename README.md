# Outfeats AI

A personalized fashion shopping assistant built with a multi-agent RAG architecture. Users can search for fashion products using natural language, get contextual recommendations, and ask general shopping questions.

---

## Architecture

```
User (Next.js / Vercel)
    ↓
FastAPI (GCP Cloud Run)
    ↓
Google ADK Agent (DeepSeek via LiteLLM)
    ├── product_recommendation tool
    │       ├── ParaphraserPipeline     — query rewriting with chat history
    │       ├── MetaDataFilterPipeline  — extract filters (color, style, fabric, pattern)
    │       ├── ProductRAGPipeline      — vector search on product catalog
    │       └── SerpAPI Image Search    — fetch product images
    └── common_information tool
            ├── MetaDataFilterPipeline  — extract filters (category, intent)
            └── CommonsRAGPipeline      — vector search on customer support docs
```

---

## Stack

| Layer | Technology |
|---|---|
| Agent | Google ADK + LiteLLM |
| LLM | DeepSeek (`deepseek-chat`) |
| RAG | Haystack 2.x + haystack-experimental |
| Embeddings | SentenceTransformers `all-MiniLM-L6-v2` |
| Vector Store | MongoDB Atlas Vector Search |
| Image Search | SerpAPI Google Images |
| Backend | FastAPI + Uvicorn |
| Frontend | Next.js 15 + Tailwind CSS |
| Backend Deploy | GCP Cloud Run (`asia-southeast2`) |
| Frontend Deploy | Vercel |

---

## Project Structure

```
smartshopper/
├── agent/
│   ├── smartshopper_agent.py   # LlmAgent definition
│   └── response_handler.py     # ADK runner
├── api/
│   ├── main.py                 # FastAPI app + CORS
│   ├── schemas.py              # Pydantic request/response models
│   └── routes/chat.py          # POST /chat endpoint
├── config/
│   └── settings.py             # Environment variable loading
├── database/
│   └── mongo_client.py         # MongoDB Atlas client + helpers
├── memory/
│   └── chat_memory.py          # InMemoryChatMessageStore
├── monitoring/
│   ├── evaluator.py            # RAGAS evaluation pipeline
│   └── report.py               # Evaluation report generation
├── pipelines/
│   ├── paraphraser.py          # Query rewriting with memory
│   ├── metadata_filter.py      # LLM-based metadata extraction
│   ├── product_rag.py          # Product retrieval + generation
│   └── common_rag.py           # Customer support retrieval + generation
├── scripts/
│   ├── preprocess_products.py  # Product data cleaning
│   ├── preprocess_commons.py   # Customer support data cleaning
│   ├── store_products.py       # Ingest products to MongoDB Atlas
│   ├── store_commons.py        # Ingest commons to MongoDB Atlas
│   └── run_evaluation.py       # Run RAGAS evaluation
├── tools/
│   ├── product_tool.py         # ADK FunctionTool for product search
│   ├── common_tool.py          # ADK FunctionTool for support queries
│   ├── image_search.py         # SerpAPI image fetch
│   └── timer.py                # Logging decorator
├── frontend/                   # Next.js app
├── Dockerfile
├── requirements.txt
└── main.py                     # Uvicorn entrypoint
```

---

## Setup

### Prerequisites

- Python 3.11
- Node.js >= 18.18.0
- Docker
- Google Cloud SDK
- MongoDB Atlas account
- DeepSeek API key
- SerpAPI key

### Environment Variables

Create `.env` from `.env.example`:

```env
MONGO_CONNECTION_STRING=
MONGO_DB_NAME=
DEEPSEEK_API=
SERP_API_KEY=
ALLOWED_ORIGINS=http://localhost:3000
```

### Backend

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

python main.py
```

### Data Ingestion

```bash
python scripts/preprocess_products.py
python scripts/store_products.py

python scripts/preprocess_commons.py
python scripts/store_commons.py
```

### MongoDB Atlas Vector Search Index

**Products collection:**
```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine" },
    { "type": "filter", "path": "meta.style" },
    { "type": "filter", "path": "meta.color" },
    { "type": "filter", "path": "meta.fabric" },
    { "type": "filter", "path": "meta.pattern" }
  ]
}
```

**Commons collection:**
```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine" },
    { "type": "filter", "path": "meta.category" },
    { "type": "filter", "path": "meta.intent" }
  ]
}
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Deployment

### Backend (GCP Cloud Run)

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/smartshopper:latest
gcloud run deploy smartshopper \
  --image gcr.io/PROJECT_ID/smartshopper:latest \
  --platform managed \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 2Gi \
  --set-env-vars MONGO_CONNECTION_STRING=...,DEEPSEEK_API=...,SERP_API_KEY=...,ALLOWED_ORIGINS=...
```

### Frontend (Vercel)

1. Push `frontend/` to GitHub
2. Import repo in Vercel dashboard
3. Set `NEXT_PUBLIC_API_URL=https://YOUR_CLOUD_RUN_URL`
4. Deploy

---

## API

### `POST /chat`

**Request:**
```json
{
  "message": "show me casual dresses under $20",
  "session_id": null
}
```

**Response:**
```json
{
  "response": "Here are some casual dresses...",
  "session_id": "uuid",
  "products": [
    {
      "name": "Tie Shoulder Layered Hem Dress",
      "price": "$21.38",
      "meta": "Style: Casual · Color: Hot Pink\nSize: S, M, L",
      "image_url": "https://..."
    }
  ]
}
```

### `GET /health`

```json
{ "status": "OK" }
```

---

## Evaluation

RAGAS evaluation using `@experiment` decorator pattern:

```bash
python scripts/run_evaluation.py
```

Results saved to `experiments/`.

---

## Author

Ryo Nurizki — Dibimbing.id Batch 41
