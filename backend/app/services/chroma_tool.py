from chromadb import PersistentClient
import os

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
client = PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("menu_items")

def get_similar_menu_items(query: str, k: int = 3) -> str:
    results = collection.query(query_texts=[query], n_results=k)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    formatted_results = []
    for doc, meta in zip(documents, metadatas):
        restaurant = meta.get("restaurant_name", "Unknown Restaurant")
        address = meta.get("restaurant_address", "Unknown Address")
        formatted_results.append(f"- {doc} (from {restaurant}, {address})")

    return "\n".join(formatted_results)
