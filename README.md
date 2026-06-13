# Outfeats AI

A personalized fashion shopping assistant built with a multi-agent RAG architecture. Users can search for fashion products using natural language, get contextual recommendations, and ask general shopping questions.

---

## Live Demo

**Web App:** [https://outfeats-frontend.vercel.app](https://outfeats-frontend.vercel.app)

Try asking:
- `"Show me casual dresses under $20"`
- `"Find floral pattern tops in blue"`
- `"What are your return and refund policies?"`
- `"Do you offer free shipping?"`

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

## Storing Strategy

### Commons Collection

Data source: [Bitext Customer Support LLM Chatbot Training Dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) — 26,872 customer support Q&A pairs across 27 intent categories.

Each document is stored with the following structure:

```
Document(
    content  = instruction,        # customer query text (used for embedding)
    meta = {
        response  : str,           # expected support answer
        category  : str,           # e.g. "ORDER", "PAYMENT", "SHIPPING"
        intent    : str            # e.g. "track_order", "payment_issue"
    }
)
```

**Embedding:** `all-MiniLM-L6-v2` (384 dimensions) via `SentenceTransformersDocumentEmbedder`.

**Duplicate policy:** `DuplicatePolicy.OVERWRITE` — re-running the store script safely overwrites existing documents by ID.

**Filter fields indexed:** `meta.category` and `meta.intent` — enables pre-filtering before vector search to narrow the retrieval scope.

### Products Collection

Each product document stores structured metadata alongside its embedding:

```
Document(
    content  = product_content,    # concatenated text for embedding
    meta = {
        name    : str,
        price   : float,
        color   : str,
        style   : str,
        fabric  : str,
        pattern : str,
        size    : list[str]
    }
)
```

**Filter fields indexed:** `meta.style`, `meta.color`, `meta.fabric`, `meta.pattern`.

---

## RAG Strategy

### Commons RAG

```
User query
    → MetaDataFilterPipeline     — LLM extracts category + intent from query
    → MongoDBAtlasEmbeddingRetriever
          pre-filter: { category: ..., intent: ... }
          vector search: cosine similarity on query embedding
    → CommonsRAGPipeline         — retrieved docs injected into prompt → DeepSeek generates answer
```

The metadata filter narrows the search space before vector similarity is computed, improving both relevance and retrieval speed. If no filters are extracted, the retriever falls back to pure vector search across all documents.

### Product RAG

```
User query
    → ParaphraserPipeline        — rewrites query using chat history for context continuity
    → MetaDataFilterPipeline     — LLM extracts color, style, fabric, pattern
    → MongoDBAtlasEmbeddingRetriever
          pre-filter: { style: ..., color: ..., fabric: ..., pattern: ... }
          vector search: cosine similarity on paraphrased query embedding
    → ProductRAGPipeline         — retrieved products injected into prompt → DeepSeek generates ranked list
    → SerpAPI                    — fetches product image for each retrieved item
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
