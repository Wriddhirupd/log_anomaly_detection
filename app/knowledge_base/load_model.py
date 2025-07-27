import os

from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings

def load_model():
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    model.save("models/minilm")
    print("Model loaded successfully.")
    return model

def test_model():
    print("Testing SentenceTransformer model...")
    model = HuggingFaceEmbeddings(model_name=os.path.join(os.getcwd(), "models", "minilm"))
    test_sentence = "This is a test sentence."
    embedding = model.embed_query(test_sentence)
    print(f"Embedding for '{test_sentence}': {embedding[:5]}...")  # Print first 5 dimensions
    return embedding

if __name__ == "__main__":
    load_model()
    test_model()