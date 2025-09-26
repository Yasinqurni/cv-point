import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from config import get_config


config = get_config()


genai.configure(api_key=config.gemini_api_key)
llm = genai.GenerativeModel(config.gemini_model)


# ==========================
# Init Embedding Model + FAISS Index
# ==========================
encoder = SentenceTransformer("all-MiniLM-L6-v2")
dimension = encoder.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dimension)
documents: list[str] = []


# ==========================
# Add documents to vector DB
# ==========================
def add_documents(docs: list[str]):
    global documents
    vectors = encoder.encode(docs)
    index.add(np.array(vectors).astype("float32"))
    documents.extend(docs)


# ==========================
# Query with RAG
# ==========================
def query_rag(question: str, top_k: int = 3) -> str:
    # Encode question
    query_vec = encoder.encode([question])
    D, I = index.search(np.array(query_vec).astype("float32"), top_k)

    # get relevant document
    context_docs = [documents[i] for i in I[0] if i < len(documents)]
    context = "\n".join(context_docs)

    # Prompt to LLM
    prompt = f"""
    Context:
    {context}

    Question:
    {question}

    Answer the question using ONLY the context above.
    """

    response = llm.generate_content(prompt)
    return response.text
