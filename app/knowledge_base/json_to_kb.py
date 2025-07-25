import json
import os
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
import ssl

# Disable SSL verification
os.environ["CURL_CA_BUNDLE"] = ""
ssl._create_default_https_context = ssl._create_unverified_context

# Path to your knowledge base JSON
KB_DIR = "app/knowledge_base"
KB_PATH = "kb.json"
FAISS_DIR = "faiss_store"

MODEL_PATH = "/Users/wriddhirupdutta/work/glp/dev-env/ws/glp-qna-search/app/ml_model"

def load_knowledge_base(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs = []
    for entry in data:
        pattern = entry["pattern"]
        solution = entry["solution"]
        doc = Document(
            page_content=pattern,
            metadata={"solution": solution}
        )
        docs.append(doc)
    return docs

def build_faiss_store(docs, faiss_path: str):
    print("Building FAISS index with SentenceTransformer embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    # embeddings = SentenceTransformerEmbeddings(MODEL_PATH)  # Using SentenceTransformer directly
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(faiss_path)
    print(f"✅ FAISS vectorstore saved at: {faiss_path}")

if __name__ == "__main__":
    kb_path = os.path.join(os.getcwd(), KB_DIR, KB_PATH)
    faiss_dir = os.path.join(os.getcwd(), KB_DIR, FAISS_DIR)
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"Knowledge base not found: {kb_path}")
    documents = load_knowledge_base(kb_path)
    build_faiss_store(documents, faiss_dir)
