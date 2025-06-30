import psycopg2
import html
from datetime import datetime
from models import Restaurant, MenuItem, RestaurantHours
from dataclasses import astuple
from psycopg2.extras import execute_values

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

    def mark_menu_item_embedded(self, menu_item_id):
        self.cur.execute("""
            UPDATE menu_items
            SET embedded = TRUE
            WHERE id = %s
        """, (menu_item_id,))

    def restaurant_exists_for_url(self, url: str) -> bool:
        self.cur.execute("SELECT 1 FROM restaurants WHERE url = %s LIMIT 1", (url,))
        return self.cur.fetchone() is not None
    
    def insert_restaurant(self, data, link):
        restaurant = Restaurant.from_json(data, link)
        self.cur.execute("""
            INSERT INTO restaurants (
                name, url, address, city, region, postal_code, country,
                latitude, longitude, telephone, rating, review_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING id
        """, astuple(restaurant))
        result = self.cur.fetchone()
        return result[0] if result else None
    
    def insert_categories(self, restaurant_id, data, link):

        if restaurant_id is None:
            print(f"⚠️ Skipping menu categories for {link} — no restaurant_id")
            return
        
        categories = data.get("servesCuisine", [])

        for category in categories:
            category = html.unescape(category)
            self.cur.execute("""
                INSERT INTO categories (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (category,))
            result = self.cur.fetchone()

            if result is None:
                self.cur.execute("SELECT id FROM categories WHERE name = %s", (category,))
                category_id = self.cur.fetchone()[0]
            else:
                category_id = result[0]

            self.cur.execute("""
                INSERT INTO restaurant_categories (restaurant_id, category_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (restaurant_id, category_id))
        
        return

    def insert_menu_items(self, restaurant_id, data, link):
        if restaurant_id is None:
            print(f"⚠️ Skipping menu items for {link} — no restaurant_id")
            return 0
        inserted = 0
        try:
            for section in data.get("hasMenu", {}).get("hasMenuSection", []):
                section_name = section.get("name", "")
                for item in section.get("hasMenuItem", []):
                    menu_item = MenuItem.from_json(restaurant_id, section_name, item)
                    self.cur.execute("""
                        INSERT INTO menu_items (
                            restaurant_id, section, name, description, price, currency, embedded
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (restaurant_id, name) DO NOTHING
                    """, astuple(menu_item))
                    if self.cur.rowcount > 0:
                        inserted += 1
        except Exception as e:
            print(f"⚠️ Menu item error at {link}: {e}")
        return inserted

    def insert_hours(self, restaurant_id, data, link):
        if restaurant_id is None:
            print(f"⚠️ Skipping hours for {link} — no restaurant_id")
            return 0
        inserted = 0
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
                    if self.cur.rowcount > 0:
                        inserted += 1
        except Exception as e:
            print(f"⚠️ Opening hours error at {link}: {e}")
        return inserted

    def insert_restaurant_data(self, data, link):
        restaurant_id = self.insert_restaurant(data, link)
        if restaurant_id is None:
            return None

        self.insert_categories(restaurant_id, data, link)
        menu_count = self.insert_menu_items(restaurant_id, data, link)
        hours_count = self.insert_hours(restaurant_id, data, link)
        
        return restaurant_id, menu_count, hours_count

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
    
    def get_restaurant_by_id(self, restaurant_id: int) -> dict | None:
        """Fetch restaurant info by ID."""
        self.cur.execute("""
            SELECT id, name, address
            FROM restaurants
            WHERE id = %s
        """, (restaurant_id,))
        row = self.cur.fetchone()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "address": row[2]
            }
        return None
    
    def get_unembedded_menu_items_by_restaurant_id(self, restaurant_id):
        self.cur.execute("""
            SELECT id, name, description
            FROM menu_items
            WHERE restaurant_id = %s AND embedded = FALSE
        """, (restaurant_id,))
        return self.cur.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()