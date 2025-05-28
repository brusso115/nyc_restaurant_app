import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import hashlib

class VectorManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="menu_items")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_and_store(self, restaurant_id, name, description):
        text = f"{name}: {description}"
        vector_id = self.deterministic_id(restaurant_id, name, description)

        # Check if this vector already exists
        try:
            existing = self.collection.get(ids=[vector_id])
            if existing and existing['ids']:
                return  # Already exists
        except:
            pass  # Safe to insert if not found

        embedding = self.model.encode(text).tolist()
        self.collection.add(
            ids=[vector_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"restaurant_id": restaurant_id}]
        )

    def deterministic_id(self, restaurant_id, name, description):
        text = f"{restaurant_id}:{name}:{description}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()
