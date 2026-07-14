# Enterprise Treasury AI Copilot

Starter FastAPI project for a source-grounded treasury and regulatory RAG application.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`.

## Run

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Available Endpoints

- `GET /health`
- `POST /documents/upload`
- `POST /chat`

## Important

This is a starter implementation. Do not upload confidential banking or client documents. Review security, privacy, governance, evaluation, and access controls before any production use.
