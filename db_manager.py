import psycopg2
import html
from datetime import datetime
from models import Restaurant, MenuItem, RestaurantHours
from dataclasses import astuple
from psycopg2.extras import execute_values
import os


DB_CONFIG = {
    "dbname": "restaurant_data",
    "user": "baileyrusso",
    "host": "localhost",
    "port": "5432"
}

class DatabaseManager:
    def __init__(self, DB_CONFIG):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()

    def get_link_id_by_url(self, url):
        self.cur.execute("""
            SELECT id FROM store_links
            WHERE url = %s
        """, (url,))
        row = self.cur.fetchone()
        return row[0] if row else None
    
    def get_link_status(self, link_id):
        self.cur.execute("""
            SELECT status FROM store_links
            WHERE id = %s
        """, (link_id,))
        row = self.cur.fetchone()
        return row[0] if row else None
    
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

    def mark_link_processing(self, link_id):
        self.cur.execute("""
            UPDATE store_links
            SET status = 'processing',
                updated_at = NOW()
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

    def get_menu_item_ids_by_restaurant_url(self, url):
        self.cur.execute("""
            SELECT mi.id
            FROM menu_items mi
            JOIN restaurants r ON mi.restaurant_id = r.id
            WHERE r.url = %s
        """, (url,))
        results = self.cur.fetchall()
        return [row[0] for row in results]
    
    def get_menu_item_by_id(self, menu_item_id):
        self.cur.execute("""
            SELECT id, restaurant_id, name, description
            FROM menu_items
            WHERE id = %s
        """, (menu_item_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "id": row[0],
                "restaurant_id": row[1],
                "name": row[2],
                "description": row[3]
            }
        return None

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()