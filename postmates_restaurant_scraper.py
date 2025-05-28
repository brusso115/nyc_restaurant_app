import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import random
from db_manager import DatabaseManager

class RestaurantScraper:
    def __init__(self, db_manager, csv_path="./data/store_links.csv"):
        self.db = db_manager
        self.csv_path = csv_path

    def load_links(self):
        df = pd.read_csv(self.csv_path)
        return df['store_link'].dropna().unique()

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
        links = self.load_links()

        for link in links:
            
            if self.db.restaurant_exists(link):
                print(f"⏭️ Skipping {link}: already in DB")
                continue

            try:
                data = self.parse_restaurant_page(link)
                if not data:
                    print(f"Skipping {link}: no JSON-LD found")
                    continue

                self.db.insert_restaurant_data(data, link)
                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                print(f"❌ Error processing {link}: {e}")

            self.db.commit()

        self.db.close()
        print("✅ All done.")


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