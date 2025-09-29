
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import pickle
from .config import get_config

config = get_config()
genai.configure(api_key=config.gemini_api_key)
llm = genai.GenerativeModel(config.gemini_model)

# ==========================
# Init Embedding Model + FAISS
# ==========================
encoder = SentenceTransformer("all-MiniLM-L6-v2")
dimension = encoder.get_sentence_embedding_dimension()
INDEX_PATH = "faiss_index.bin"
DOCS_PATH = "faiss_docs.pkl"

def load_index_and_docs():
    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(DOCS_PATH, "rb") as f:
            documents = pickle.load(f)
        return index, documents
    else:
        return faiss.IndexFlatL2(dimension), []

def save_index_and_docs(index, documents):
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

index, documents = load_index_and_docs()


# ==========================
# Add documents to vector DB
# ==========================

def add_documents(docs: list[str]):
    global documents, index
    vectors = encoder.encode(docs)
    index.add(np.array(vectors).astype("float32"))
    documents.extend(docs)
    save_index_and_docs(index, documents)


# ==========================
# Query with RAG
# ==========================

def query_rag(question: str, top_k: int = 3) -> str:
    if not documents or index.ntotal == 0:
        context = ""
    else:
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
