# FALSA

FALSA is an async FastAPI backend for WhatsApp-based AI travel customer service.
It stores conversations in Supabase, retrieves short-term chat context, uses Groq
with Hugging Face fallback, calls local tools for FALSA info/trip search/booking
leads, stores vector embeddings in Supabase with Jina Embeddings, and sends replies
through Meta WhatsApp Cloud API.

## Quick Start

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

Run checks:

```bash
pytest
ruff check .
```

## Main Endpoints

- `GET /healthz`
- `GET /webhooks/whatsapp`
- `POST /webhooks/whatsapp`
- `POST /admin/seed-info`
- `POST /admin/sync-trips`

Apply the SQL in `supabase/migrations` to create the Supabase schema, including the
pgvector tables and RPC functions, before using the production services.
