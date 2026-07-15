# Enterprise Treasury AI Copilot

> An enterprise Retrieval-Augmented Generation (RAG) application for treasury, liquidity, capital, and regulatory document intelligence.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.5-black)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## Overview

Enterprise Treasury AI Copilot is an end-to-end Retrieval-Augmented Generation (RAG) system that enables users to upload treasury and regulatory PDF documents and ask natural language questions while receiving grounded answers with page-level citations.

The project was designed to demonstrate production-oriented AI engineering practices including:

- Enterprise RAG architecture
- Vector search
- Citation grounding
- Prompt engineering
- FastAPI backend development
- Streamlit frontend
- OpenAI Responses API integration
- ChromaDB semantic search
- Conversation memory
- Explainable AI responses

Unlike a general-purpose chatbot, every answer is grounded in the uploaded regulatory documents.

---

# Demo

## Upload Documents

- Upload PDF regulatory documents
- Automatic text extraction
- Paragraph-aware chunking
- Embedding generation
- Vector indexing

## Ask Questions

Example questions:

> What is the treatment of committed liquidity facilities?

> Explain the Liquidity Coverage Ratio.

> Compare committed liquidity facilities with excluded facilities.

> Summarize the requirements in one paragraph.

Every answer contains page-level citations.

---

# Features

## Current

- PDF upload
- PDF parsing
- Paragraph-aware chunking
- OpenAI embeddings
- ChromaDB vector database
- Semantic retrieval
- FastAPI REST API
- Streamlit web interface
- Grounded responses
- Citation filtering
- Page-level evidence
- Conversation memory
- Similarity filtering
- Configurable retrieval (Top-K)

---

## Planned

- Query rewriting
- Hybrid search (BM25 + embeddings)
- Cross-document reasoning
- Multi-document collections
- RAG evaluation dashboard
- Docker deployment
- Authentication
- Azure OpenAI support
- Conversation persistence
- Cloud deployment

---

# Architecture

```
                        Streamlit UI
                              │
                              ▼
                     FastAPI Backend
                              │
         ┌────────────────────┼─────────────────────┐
         │                    │                     │
         ▼                    ▼                     ▼
  Document Upload      Chat Endpoint        Health Endpoint
         │
         ▼
 PDF Processing Service
         │
         ▼
 Paragraph-aware Chunking
         │
         ▼
 OpenAI Embeddings
         │
         ▼
      ChromaDB
         │
         ▼
 Semantic Retrieval
         │
         ▼
 Prompt Builder
         │
         ▼
 OpenAI GPT-5.5
         │
         ▼
 Citation Filtering
         │
         ▼
 Final Grounded Answer
```

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Backend | FastAPI |
| Frontend | Streamlit |
| LLM | OpenAI GPT-5.5 |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Database | ChromaDB |
| PDF Processing | PyMuPDF |
| Validation | Pydantic |
| HTTP Client | Requests |
| Version Control | Git |

---

# Project Structure

```
enterprise-treasury-ai-copilot/

├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── prompts/
│   ├── routes/
│   ├── services/
│   └── utils/
│
├── frontend/
│   └── streamlit_app.py
│
├── data/
│   ├── uploads/
│   ├── chroma/
│   └── sample_doc/
│
├── docs/
│   ├── architecture.md
│   └── screenshots/
│
├── tests/
│
├── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/enterprise-treasury-ai-copilot.git

cd enterprise-treasury-ai-copilot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create an environment file

```bash
cp .env.example .env
```

Add your OpenAI API key

```text
OPENAI_API_KEY=your_key_here
```

---

# Running the Backend

```bash
uvicorn app.main:app --reload
```

Swagger UI

```
http://127.0.0.1:8000/docs
```

---

# Running the Frontend

```bash
streamlit run frontend/streamlit_app.py
```

Open

```
http://localhost:8501
```

---

# API Endpoints

## Upload Document

```
POST /documents/upload
```

Uploads and indexes a PDF.

---

## Chat

```
POST /chat
```

Returns a grounded answer with citations.

---

## Health Check

```
GET /health
```

Returns backend status.

---

# Example Workflow

1. Upload a regulatory PDF
2. Extract text
3. Chunk document
4. Generate embeddings
5. Store vectors in ChromaDB
6. Ask a question
7. Retrieve relevant chunks
8. Generate grounded response
9. Return page-level citations

---

# Example Output

```
Question:

What is the treatment of committed liquidity facilities?

↓

Answer:

Committed liquidity facilities to financial institutions must
assume a 100% drawdown of the undrawn amount for LCR purposes.

Supporting Sources

Source 1
Page 47

Source 2
Page 45
```

---

# Design Principles

This project emphasizes:

- Grounded AI responses
- Explainability
- Retrieval transparency
- Modular architecture
- Production-oriented engineering
- Enterprise software design
- Extensibility
- Maintainability

---

# Future Improvements

- Context-aware query rewriting
- Hybrid retrieval
- Cross-document reasoning
- Citation highlighting inside PDFs
- Evaluation dashboard
- Retrieval precision metrics
- Hallucination detection
- Docker
- Kubernetes deployment
- Azure OpenAI integration
- Authentication
- PostgreSQL conversation history

---

# Why This Project

This project demonstrates practical AI engineering skills relevant to enterprise AI applications, including:

- Retrieval-Augmented Generation (RAG)
- Large Language Model integration
- Vector databases
- API development
- Prompt engineering
- AI application architecture
- Explainable AI
- Citation grounding
- Enterprise document intelligence

---

# Disclaimer

This project is intended for educational and portfolio purposes.

It is **not** a replacement for professional legal, regulatory, compliance, treasury, or risk advice.

---

# Author

**Libo Luo**

Master of Management in Artificial Intelligence (MMAI)

17+ years of Financial Services Transformation

Capital Markets • Treasury • Basel III • AI Engineering

---
