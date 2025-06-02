import psycopg2
import html
from datetime import datetime
from models import Restaurant, MenuItem, RestaurantHours
from dataclasses import astuple
from psycopg2.extras import execute_values

class DatabaseManager:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()

    # def restaurant_exists(self, url):
    #     self.cur.execute("SELECT 1 FROM restaurants WHERE url = %s", (url,))
    #     return self.cur.fetchone() is not None
    
    def insert_store_links(self, link_tuples):

        if not link_tuples:
            return

        query = """
        INSERT INTO store_links (url, address, status)
        VALUES %s
        ON CONFLICT (url) DO NOTHING;
        """
        execute_values(self.cur, query, link_tuples)
        print(f"✅ Inserted {len(link_tuples)} new store_links")

    def fetch_pending_links(self, limit=50):
        self.cur.execute("""
            SELECT id, url
            FROM store_links
            WHERE status = 'pending'
            ORDER BY updated_at ASC
            LIMIT %s
            FOR UPDATE SKIP LOCKED
        """, (limit,))
        return self.cur.fetchall()

    def mark_link_processing(self, link_id):
        self.cur.execute("""
            UPDATE store_links
            SET status = 'processing', updated_at = NOW()
            WHERE id = %s
        """, (link_id,))

    def mark_link_done(self, link_id):
        self.cur.execute("""
            UPDATE store_links
            SET status = 'done', last_scraped = NOW(), updated_at = NOW(), error = NULL
            WHERE id = %s
        """, (link_id,))

    def mark_link_failed(self, link_id, error):
        self.cur.execute("""
            UPDATE store_links
            SET status = 'failed', error = %s, updated_at = NOW()
            WHERE id = %s
        """, (error, link_id))
    
    def insert_restaurant(self, data, link):
        restaurant = Restaurant.from_json(data, link)
        self.cur.execute("""
            INSERT INTO restaurants (
                name, url, categories, address, city, region, postal_code, country,
                latitude, longitude, telephone, rating, review_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING id
        """, astuple(restaurant))
        result = self.cur.fetchone()
        return result[0] if result else None

    def insert_menu_items(self, restaurant_id, data, link):
        try:
            for section in data.get("hasMenu", {}).get("hasMenuSection", []):
                section_name = section.get("name", "")
                for item in section.get("hasMenuItem", []):
                    menu_item = MenuItem.from_json(restaurant_id, section_name, item)
                    self.cur.execute("""
                        INSERT INTO menu_items (
                            restaurant_id, section, name, description, price, currency
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (restaurant_id, name) DO NOTHING
                    """, astuple(menu_item))
        except Exception as e:
            print(f"⚠️ Menu item error at {link}: {e}")

    def insert_hours(self, restaurant_id, data, link):
        try:
            for entry in data.get("openingHoursSpecification", []):
                days = entry["dayOfWeek"]
                if isinstance(days, str):
                    days = [days]
                for day in days:
                    restaurant_hours = RestaurantHours.from_json(restaurant_id, day, entry)
                    self.cur.execute("""
                        INSERT INTO restaurant_hours (restaurant_id, day, opens, closes)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT ON CONSTRAINT unique_hours DO NOTHING
                    """, astuple(restaurant_hours))
        except Exception as e:
            print(f"⚠️ Opening hours error at {link}: {e}")

    def insert_restaurant_data(self, data, link):
        restaurant_id = self.insert_restaurant(data, link)
        self.insert_menu_items(restaurant_id, data, link)
        self.insert_hours(restaurant_id, data, link)
        print(f"✅ Inserted {html.unescape(data['name'])}")

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()