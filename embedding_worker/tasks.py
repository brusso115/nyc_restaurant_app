from common.db_manager import DatabaseManager
import traceback
import chromadb
from sentence_transformers import SentenceTransformer
from celery.signals import worker_process_init
import threading
from celery import Celery
import os

app = Celery("embedder_worker", broker="redis://localhost:6379/0")

app.conf.task_routes = {
    "embedding_worker.tasks.embed_menu_items_task": {"queue": "embedding_queue"}
}

app.conf.broker_connection_retry_on_startup = True 

sentence_model = None
_model_lock = threading.Lock()

DB_CONFIG = {
    "dbname": "restaurant_data",
    "user": "baileyrusso",
    "host": "localhost",
    "port": "5432"
}

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db"))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "sentence_transformer_model"))

def ensure_model_loaded():
    global sentence_model
    if sentence_model is None:
        with _model_lock:
            if sentence_model is None:  # Double-checked locking
                print("🔁 Loading SentenceTransformer model...")
                sentence_model = SentenceTransformer(MODEL_PATH)

@worker_process_init.connect
def init_worker(**kwargs):
    ensure_model_loaded()

def embed_items(db: DatabaseManager, items: list[dict], link_id: int):

    texts = [item["text"] for item in items]
    embeddings = sentence_model.encode(texts, show_progress_bar=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH, tenant="default_tenant")
    collection = client.get_or_create_collection("menu_items")

    collection.add(
        documents=texts,
        ids=[str(item["id"]) for item in items],
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "menu_item_id": str(item["id"]),
                "restaurant_name": item["restaurant_name"],
                "restaurant_address": item["restaurant_address"],
            }
            for item in items
        ]
    )

    for item in items:
        db.cur.execute("UPDATE menu_items SET embedded = TRUE WHERE id = %s", (item["id"],))

    db.mark_link_done(link_id)

@app.task(name="embedding_worker.tasks.embed_menu_items_task", queue="embedding_queue")
def embed_menu_items_task(menu_item_ids, link_id):

    ensure_model_loaded()
    db = DatabaseManager(DB_CONFIG)

    try: 
        items = []
        for item_id in menu_item_ids:
            item = db.get_menu_item_by_id(item_id)
            if item:
                restaurant = db.get_restaurant_by_id(item["restaurant_id"])
                if restaurant:
                    text = f"{item['name']} - {item['description'] or ''}"
                    items.append({
                        "id": item_id,
                        "text": text,
                        "restaurant_name": restaurant["name"],
                        "restaurant_address": restaurant["address"]
                    })
                else:
                    raise ValueError(f"No restaurant found for menu_item_id {item_id}")

        embed_items(db, items, link_id)
        db.commit()

    except Exception as e:
        print(f"❌ Embedding task failed for link_id {link_id}: {e}")
        traceback.print_exc()
        db.mark_link_failed(link_id, f"Embedding error: {e}")
        db.commit()
    finally:
        db.close()