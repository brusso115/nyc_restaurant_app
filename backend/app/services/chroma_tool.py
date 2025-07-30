from chromadb import PersistentClient
import os

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
client = PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("menu_items")

def get_similar_menu_items(query: str, k: int = 5) -> str:
    results = collection.query(query_texts=[query], n_results=k)
    items = results["documents"][0]
    return "\n".join(f"- {item}" for item in items)
