import os
from common.db_manager import DatabaseManager
import traceback
import requests
import json
from bs4 import BeautifulSoup
import time
import random
import html
from celery import Celery

app = Celery("scraper_worker", broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))

app.conf.task_routes = {
    "scraper_worker.tasks.scrape_restaurant_task": {"queue": "scraper_queue"}
}

app.conf.broker_connection_retry_on_startup = True 

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "password": os.getenv("DB_PASSWORD"),
}

def parse_json_ld(url: str) -> dict:
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    tag = soup.find("script", type="application/ld+json")
    if not tag:
        raise ValueError("No JSON-LD script tag found")
    return json.loads(tag.string)

@app.task(name="scraper_worker.tasks.scrape_restaurant_task")
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
            
            try:
                result = app.send_task(
                    "embedding_worker.tasks.embed_menu_items_task",
                    args=[item_ids, link_id],
                    queue="embedding_queue"
                )
                print(f"🚀 Enqueued embedding task {result.id}")
            except Exception as e:
                print(f"❌ Failed to enqueue embedding task: {e}")

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