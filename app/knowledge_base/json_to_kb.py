import json
import os
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

# Path to your knowledge base JSON
KB_DIR = "app/knowledge_base"
KB_PATH = "kb.json"
FAISS_DIR = "faiss_store"

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
    embeddings = HuggingFaceEmbeddings(model_name=os.path.join(os.getcwd(), "models", "minilm"))
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(faiss_path)
    print(f"FAISS vectorstore saved at: {faiss_path}")
    return db

def load_faiss_store():
    kb_path = os.path.join(os.getcwd(), KB_DIR, KB_PATH)
    if not os.path.exists(KB_DIR):
        raise FileNotFoundError(f"Knowledge base directory not found: {KB_DIR}")

    faiss_dir = os.path.join(os.getcwd(), KB_DIR, FAISS_DIR)
    if not os.path.exists(faiss_dir):
        os.makedirs(faiss_dir)
        print(f"Knowledge base not found: {kb_path}")
        documents = load_knowledge_base(kb_path)
        print(f"Loaded {documents} documents from knowledge base.")
        db = build_faiss_store(documents, faiss_dir)
    else:
        print(f"Knowledge base already exists at: {faiss_dir}")
        db = FAISS.load_local(faiss_dir,
                              HuggingFaceEmbeddings(model_name=os.path.join(os.getcwd(), "models", "minilm")),
                              allow_dangerous_deserialization=True)
    return db

if __name__ == "__main__":
    load_faiss_store()
