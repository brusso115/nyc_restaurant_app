from celery_app import app
from db_manager import DatabaseManager
import traceback
import requests
import json
from bs4 import BeautifulSoup
import time
import random
import chromadb
from sentence_transformers import SentenceTransformer
from celery.signals import worker_process_init
import threading
import html

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

def parse_json_ld(url: str) -> dict:
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    tag = soup.find("script", type="application/ld+json")
    if not tag:
        raise ValueError("No JSON-LD script tag found")
    return json.loads(tag.string)

def embed_items(db: DatabaseManager, items: list[tuple[int, str]], link_id: int):

    texts = [text for _, text in items]
    embeddings = sentence_model.encode(texts, show_progress_bar=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection("menu_items")

    collection.add(
        documents=texts,
        ids=[str(item_id) for item_id, _ in items],
        embeddings=embeddings.tolist(),
    )

    for item_id, _ in items:
        db.cur.execute("UPDATE menu_items SET embedded = TRUE WHERE id = %s", (item_id,))
    db.mark_link_done(link_id)

@app.task(name="tasks.scrape_restaurant_task", queue="scraper_queue")
def scrape_restaurant_task(url, sleep_min=1.5, sleep_max=3.0):

    delay = random.uniform(sleep_min, sleep_max)
    time.sleep(delay)

    db = DatabaseManager(DB_CONFIG)
    link_id = None

    try:
        link_id = db.get_link_id_by_url(url)
        if not link_id:
            print(f"⚠️ No matching store_links row for {url}")
            return
        
        if db.restaurant_exists_for_url(url):
            print(f"⚠️ Restaurant already exists — skipping {url}")
            return

        db.mark_link_processing(link_id)
        db.commit()

        data = parse_json_ld(url)

        if not data:
            raise Exception("No data extracted")
        
        result = db.insert_restaurant_data(data, url)
        
        restaurant_id, menu_count, hours_count = result
        if menu_count == 0 or hours_count == 0:
            raise ValueError("Menu items or hours not inserted")
        
        item_ids = [row[0] for row in db.get_unembedded_menu_items_by_restaurant_id(restaurant_id)]

        if item_ids:
            embed_menu_items_task.delay(item_ids, link_id)
        else:
            print(f"⚠️ No unembedded items for {url}")

        print(f"✅ Inserted {html.unescape(data['name'])}")
        db.commit()

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        traceback.print_exc()
        db.mark_link_failed(link_id, str(e))
        db.commit()
    finally:
        db.close()

@app.task(name="tasks.embed_menu_items_task", queue="embedding_queue")
def embed_menu_items_task(menu_item_ids, link_id):

    ensure_model_loaded()
    db = DatabaseManager(DB_CONFIG)

    try: 
        items = []
        for item_id in menu_item_ids:
            item = db.get_menu_item_by_id(item_id)
            if item:
                text = f"{item['name']} - {item['description'] or ''}"
                items.append((item_id, text))

        embed_items(db, items, link_id)
        db.commit()

    except Exception as e:
        print(f"❌ Embedding task failed for link_id {link_id}: {e}")
        traceback.print_exc()
        db.mark_link_failed(link_id, f"Embedding error: {e}")
        db.commit()
    finally:
        db.close()