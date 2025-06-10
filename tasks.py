from celery_app import app
from db_manager import DatabaseManager
import traceback
import requests
import json
from bs4 import BeautifulSoup
import time
import random
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer
from celery.signals import worker_process_init
import threading

sentence_model = None
_model_lock = threading.Lock()

DB_CONFIG = {
    "dbname": "restaurant_data",
    "user": "baileyrusso",
    "host": "localhost",
    "port": "5432"
}

CHROMA_PATH = "./chroma_db"

def ensure_model_loaded():
    global sentence_model
    if sentence_model is None:
        with _model_lock:
            if sentence_model is None:  # Double-checked locking
                print("🔁 Loading SentenceTransformer model...")
                sentence_model = SentenceTransformer("./sentence_transformer_model")

@worker_process_init.connect
def init_worker(**kwargs):
    ensure_model_loaded()

@app.task(name="tasks.scrape_restaurant_task", queue="scraper_queue")
def scrape_restaurant_task(url, sleep_min=1.5, sleep_max=3.0):

    delay = random.uniform(sleep_min, sleep_max)
    time.sleep(delay)

    db = DatabaseManager(DB_CONFIG)

    try:

        link_id = db.get_link_id_by_url(url)
        if not link_id:
            print(f"⚠️ No matching store_links row for {url}")
            return

        db.mark_link_processing(link_id)

        try:
            html = requests.get(url, timeout=15).text
            soup = BeautifulSoup(html, "html.parser")
            tag = soup.find("script", type="application/ld+json")
            if not tag:
                return None
            data = json.loads(tag.string)
        except Exception:
            data = None
        
        if not data:
            db.mark_link_failed(link_id, "No JSON-LD found")
            return

        db.insert_restaurant_data(data, url)

        # Enqueue embedding tasks
        menu_item_ids = db.get_menu_item_ids_by_restaurant_url(url)
        for item_id in menu_item_ids:
            print('add task to embedding queue')
            embed_menu_item_task.delay(item_id)


        db.mark_link_done(link_id)
        db.commit()

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        db.mark_link_failed(link_id, str(e))
        db.commit()
    finally:
        db.close()

@app.task(name="tasks.embed_menu_item_task", queue="embedding_queue")
def embed_menu_item_task(menu_item_id):

    ensure_model_loaded()
    # Embed logic goes here
    print('Embedding Q Started')
    try:

        db = DatabaseManager(DB_CONFIG)
        item = db.get_menu_item_by_id(menu_item_id)

        if not item:
            print(f"⚠️ Menu item with ID {menu_item_id} not found.")
            return

        restaurant_id = item["restaurant_id"]
        name = item["name"]
        description = item["description"]
        text = f"{name}: {description or ''}"

        # Create deterministic ID
        vector_id = hashlib.md5(f"{restaurant_id}:{name}:{description or ''}".encode("utf-8")).hexdigest()

        # Initialize Chroma
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name="menu_items")

        # Check for duplicates
        existing_ids = set()
        try:
            existing_ids = set(collection.get()["ids"])
        except:
            pass

        if vector_id in existing_ids:
            print(f"🔁 Menu item already embedded: {name}")
            return

        # Embed and insert
        embedding = sentence_model.encode([text])[0].tolist()

        collection.add(
            ids=[vector_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"restaurant_id": restaurant_id}]
        )

        db.mark_menu_item_embedded(menu_item_id)

        print(f"✅ Embedded and stored: {name}")

    except Exception as e:
        print(f"❌ Failed to embed menu item {menu_item_id}: {e}")
    finally:
        db.close()