from celery_app import app
from db_manager import DatabaseManager
import traceback
import requests
import json
from bs4 import BeautifulSoup
import time
import random

DB_CONFIG = {
    "dbname": "restaurant_data",
    "user": "baileyrusso",
    "host": "localhost",
    "port": "5432"
}

@app.task(name="tasks.scrape_restaurant_task")
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
        db.mark_link_done(link_id)
        db.commit()

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        db.mark_link_failed(link_id, str(e))
        db.commit()
    finally:
        db.close()