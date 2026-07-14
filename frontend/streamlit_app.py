import os
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.getenv(
    "TREASURY_API_URL",
    "http://127.0.0.1:8000",
)

st.set_page_config(
    page_title="Enterprise Treasury AI Copilot",
    page_icon="🏦",
    layout="wide",
)

def check_api_health() -> tuple[bool, dict[str, Any] | None]:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException:
        return False, None

def upload_document(uploaded_file) -> dict[str, Any]:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf",
        )
    }
    response = requests.post(
        f"{API_BASE_URL}/documents/upload",
        files=files,
        timeout=180,
    )
    response.raise_for_status()
    return response.json()

def ask_question(
    question: str,
    top_k: int,
    conversation_history: list[dict[str, str]],
) -> dict[str, Any]:
    payload = {
        "question": question,
        "top_k": top_k,
        "conversation_history": conversation_history,
    }

    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload,
        timeout=180,
    )

    response.raise_for_status()
    return response.json()

st.title("Enterprise Treasury AI Copilot")
st.caption(
    "Source-grounded AI for treasury, liquidity, capital, "
    "risk, and regulatory document analysis."
)

api_healthy, health_details = check_api_health()

if api_healthy:
    st.success("FastAPI backend is connected.")
else:
    st.error(
        "The FastAPI backend is not reachable. Start it with: "
        "`uvicorn app.main:app --reload`"
    )

with st.sidebar:
    st.header("System settings")
    st.text_input("FastAPI URL", value=API_BASE_URL, disabled=True)
    top_k = st.slider(
        "Retrieved source chunks",
        min_value=1,
        max_value=10,
        value=5,
    )
    if health_details:
        st.subheader("Backend configuration")
        st.write(f"**Chat model:** {health_details.get('chat_model', 'Unknown')}")
        st.write(
            f"**Embedding model:** "
            f"{health_details.get('embedding_model', 'Unknown')}"
        )
    st.divider()
    st.warning(
        "Use public or synthetic documents only. Do not upload "
        "confidential bank, client, employee, or customer data."
    )

upload_tab, chat_tab, about_tab = st.tabs(
    ["Upload Documents", "Ask Questions", "About"]
)

with upload_tab:
    st.subheader("Upload and index a PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        st.write(f"**Selected file:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024 / 1024:.2f} MB")

        if st.button(
            "Upload and index document",
            type="primary",
            disabled=not api_healthy,
        ):
            with st.spinner(
                "Extracting text, creating chunks, generating "
                "embeddings, and indexing the document..."
            ):
                try:
                    result = upload_document(uploaded_file)
                    st.success(
                        f"{result['document_name']} was indexed successfully."
                    )
                    c1, c2 = st.columns(2)
                    c1.metric("Chunks created", result.get("chunks_created", 0))
                    c2.metric("Status", result.get("status", "Unknown"))
                except requests.HTTPError as exc:
                    try:
                        detail = exc.response.json().get("detail")
                    except Exception:
                        detail = str(exc)
                    st.error(f"Document upload failed: {detail}")
                except requests.RequestException as exc:
                    st.error(f"Could not connect to the backend: {exc}")

with chat_tab:
    st.subheader("Ask a grounded question")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            citations = message.get("citations", [])
            if citations:
                with st.expander(
                    f"View {len(citations)} supporting source(s)"
                ):
                    for citation in citations:
                        st.markdown(
                            f"### Source {citation.get('citation_number')}"
                        )
                        st.write(
                            f"**Document:** "
                            f"{citation.get('document_name', 'Unknown document')}"
                        )
                        st.write(
                            f"**Page:** {citation.get('page_number', 'Unknown')}"
                        )
                        st.info(citation.get("excerpt", ""))

    question = st.chat_input(
        "Ask a question about the indexed documents..."
    )

    if question:
        conversation_history = [
            {
                "role": message["role"],
                "content": message["content"],
        }
        for message in st.session_state.messages[-6:]
        ]
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(
                "Retrieving evidence and generating an answer..."
            ):
                try:
                    result = ask_question(
                        question=question,
                        top_k=top_k,
                        conversation_history=conversation_history,
                    )
                    answer = result.get("answer", "No answer was returned.")
                    citations = result.get("citations", [])
                    retrieved_chunks = result.get("retrieved_chunks", 0)

                    st.markdown(answer)
                    st.caption(
                        f"Retrieved chunks considered: {retrieved_chunks}"
                    )

                    if citations:
                        with st.expander(
                            f"View {len(citations)} supporting source(s)"
                        ):
                            for citation in citations:
                                st.markdown(
                                    f"### Source "
                                    f"{citation.get('citation_number')}"
                                )
                                st.write(
                                    f"**Document:** "
                                    f"{citation.get('document_name', 'Unknown document')}"
                                )
                                st.write(
                                    f"**Page:** "
                                    f"{citation.get('page_number', 'Unknown')}"
                                )
                                st.info(citation.get("excerpt", ""))

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "citations": citations,
                        }
                    )
                except requests.HTTPError as exc:
                    try:
                        detail = exc.response.json().get("detail")
                    except Exception:
                        detail = str(exc)
                    st.error(f"The backend returned an error: {detail}")
                except requests.RequestException as exc:
                    st.error(f"Could not connect to the backend: {exc}")

    if st.session_state.messages and st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

with about_tab:
    st.subheader("How the application works")
    st.markdown(
        """
1. A PDF is uploaded to the FastAPI backend.
2. The document is parsed page by page.
3. Paragraph-aware chunks are created.
4. OpenAI embeddings are generated.
5. Chunks and metadata are stored in ChromaDB.
6. A user question is embedded and matched to indexed chunks.
7. Relevant evidence is sent to the language model.
8. The answer is returned with page-level citations.
"""
    )

    st.subheader("Current capabilities")
    st.markdown(
        """
- PDF ingestion
- Paragraph-aware chunking
- Vector search
- Similarity filtering
- Grounded answer generation
- Citation filtering
- Page-level evidence
- FastAPI backend
- Streamlit frontend
"""
    )

    st.subheader("Current limitations")
    st.markdown(
        """
- Local single-user deployment
- No authentication
- No document catalog
- No document deletion endpoint
- No conversation persistence
- No formal RAG evaluation dashboard
- No production security controls
"""
    )
