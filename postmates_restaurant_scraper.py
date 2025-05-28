import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import random
from datetime import datetime
from db_manager import DatabaseManager
from vector_manager import VectorManager
import html

class RestaurantScraper:
    def __init__(self, db_manager, vector_manager, csv_path="./data/store_links.csv"):
        self.db = db_manager
        self.vdb = vector_manager
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

                restaurant = {
                    "name": html.unescape(data["name"]),
                    "url": link,
                    "categories": html.unescape(", ".join(data.get("servesCuisine", []))),
                    "address": data["address"]["streetAddress"],
                    "city": data["address"]["addressLocality"],
                    "region": data["address"]["addressRegion"],
                    "postal_code": data["address"]["postalCode"],
                    "country": data["address"]["addressCountry"],
                    "latitude": data["geo"]["latitude"],
                    "longitude": data["geo"]["longitude"],
                    "telephone": data.get("telephone"),
                    "rating": data.get("aggregateRating", {}).get("ratingValue"),
                    "review_count": data.get("aggregateRating", {}).get("reviewCount"),
                }

                restaurant_id = self.db.insert_restaurant(restaurant)

                try:
                    for section in data.get("hasMenu", {}).get("hasMenuSection", []):
                        for item in section.get("hasMenuItem", []):
                            self.db.insert_menu_item(restaurant_id, section.get("name"), item)
                            name = html.unescape(item.get("name", ""))
                            desc = html.unescape(item.get("description", ""))
                            if name:
                                self.vdb.embed_and_store(restaurant_id, name, desc)
                except Exception as e:
                    print(f"⚠️ Menu item error at {link}: {e}")

                try:
                    for entry in data.get("openingHoursSpecification", []):
                        days = entry["dayOfWeek"]
                        if isinstance(days, str):
                            days = [days]
                        for day in days:
                            open_time = datetime.strptime(entry["opens"], "%H:%M").time()
                            close_time = datetime.strptime(entry["closes"], "%H:%M").time()
                            self.db.insert_hours(restaurant_id, day, open_time, close_time)
                except Exception as e:
                    print(f"⚠️ Opening hours error at {link}: {e}")

                print(f"✅ Inserted {html.unescape(data['name'])}")
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
    vdb = VectorManager()
    scraper = RestaurantScraper(db, vdb)
    scraper.run()