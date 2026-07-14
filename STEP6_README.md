# Step 6 — Streamlit Frontend

This package adds a Streamlit user interface to the existing Enterprise Treasury AI Copilot FastAPI project.

## Copy into your project

Copy the `frontend` folder into the project root:

```text
enterprise-treasury-ai-copilot/
├── app/
├── frontend/
│   └── streamlit_app.py
├── data/
├── docs/
└── requirements.txt
```

## Install dependencies

```bash
pip install streamlit requests
```

Add these lines to `requirements.txt`:

```text
streamlit
requests
```

## Run the backend

In Terminal 1:

```bash
uvicorn app.main:app --reload
```

## Run the frontend

In Terminal 2, from the same project root:

```bash
streamlit run frontend/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

Do not upload confidential banking, client, employee, or customer data.
