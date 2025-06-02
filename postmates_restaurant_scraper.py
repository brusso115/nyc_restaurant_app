import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import random
from db_manager import DatabaseManager

class RestaurantScraper:
    def __init__(self, db_manager):
        self.db = db_manager

    def parse_restaurant_page(self, url):
        try:
            html = requests.get(url, timeout=15).text
            soup = BeautifulSoup(html, "html.parser")
            tag = soup.find("script", type="application/ld+json")
            if not tag:
                return None
            return json.loads(tag.string)
        except Exception:
            return None

    def run(self):
        print("🔍 Fetching pending links...")
        links = self.db.fetch_and_claim_pending_links()

        for link_id, url in links:
            print(f"➡️ Processing: {url}")

            try:
                data = self.parse_restaurant_page(url)

                if not data:
                    print(f"⚠️ No structured data found in {url}")
                    self.db.mark_link_failed(link_id, error="No JSON-LD found")
                    continue

                self.db.insert_restaurant_data(data, url)
                self.db.mark_link_done(link_id)

                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                print(f"❌ Error processing {url}: {e}")
                self.db.mark_link_failed(link_id, error=str(e))

            self.db.commit()

        self.db.close()
        print("✅ Done scraping all pending links.")

if __name__ == "__main__":
    db_config = {
        "dbname": "restaurant_data",
        "user": "baileyrusso",
        "host": "localhost",
        "port": "5432"
    }
    db = DatabaseManager(db_config)
    scraper = RestaurantScraper(db)
    scraper.run()