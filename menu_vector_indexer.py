import psycopg2
from sentence_transformers import SentenceTransformer
import hashlib
from dataclasses import dataclass
from typing import List
from tqdm import tqdm
import chromadb

@dataclass
class MenuItemForEmbedding:
    id: int
    restaurant_id: int
    name: str
    description: str

class MenuItemEmbedder:
    def __init__(self, 
                 db_config: dict,
                 chroma_directory: str = "./chroma_db",
                 batch_size: int = 256):
        self.batch_size = batch_size
        self.db_config = db_config
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="menu_items")
        self.conn = psycopg2.connect(**self.db_config)
        self.cur = self.conn.cursor()

    def make_deterministic_id(self, restaurant_id, name, description):
        text = f"{restaurant_id}:{name}:{description or ''}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def fetch_menu_items(self) -> List[MenuItemForEmbedding]:
        self.cur.execute("""
            SELECT id, restaurant_id, name, description
            FROM menu_items
        """)
        rows = self.cur.fetchall()
        return [MenuItemForEmbedding(*row) for row in rows]

    def get_existing_ids(self):
        try:
            all_vectors = self.collection.get()
            return set(all_vectors["ids"])
        except:
            return set()

    def embed_and_store(self):
        items = self.fetch_menu_items()
        existing_ids = self.get_existing_ids()

        # Filter items to embed only new ones
        items_to_embed = []
        for item in items:
            vector_id = self.make_deterministic_id(item.restaurant_id, item.name, item.description)
            if vector_id not in existing_ids:
                text = f"{item.name}: {item.description or ''}"
                items_to_embed.append((vector_id, text, item.restaurant_id))

        print(f"🧠 Embedding {len(items_to_embed)} new items...")

        batch = []
        for i, (vector_id, text, restaurant_id) in enumerate(tqdm(items_to_embed, desc="Embedding")):
            batch.append((vector_id, text, restaurant_id))
            if len(batch) == self.batch_size:
                self._process_batch(batch)
                batch = []

        if batch:
            self._process_batch(batch)

        print("✅ Finished embedding and inserting into Chroma.")

    def _process_batch(self, batch):
        ids, docs, metas = zip(*[(vid, txt, {"restaurant_id": rid}) for vid, txt, rid in batch])
        embeddings = self.model.encode(docs).tolist()
        self.collection.add(ids=list(ids), embeddings=embeddings, documents=list(docs), metadatas=list(metas))

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    db_config = {
        "dbname": "restaurant_data",
        "user": "baileyrusso",
        "host": "localhost",
        "port": "5432"
    }

    embedder = MenuItemEmbedder(db_config)
    embedder.embed_and_store()
    embedder.close()
