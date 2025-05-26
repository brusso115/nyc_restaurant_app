import psycopg2

class DatabaseManager:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()

    def insert_restaurant(self, restaurant):
        self.cur.execute("""
            INSERT INTO restaurants (
                name, url, categories, address, city, region, postal_code, country,
                latitude, longitude, telephone, rating, review_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING id
        """, tuple(restaurant.values()))
        result = self.cur.fetchone()
        return result[0] if result else None
    
    def restaurant_exists(self, url):
        self.cur.execute("SELECT 1 FROM restaurants WHERE url = %s", (url,))
        return self.cur.fetchone() is not None


    def insert_menu_item(self, restaurant_id, section, item):
        self.cur.execute("""
            INSERT INTO menu_items (
                restaurant_id, section, name, description, price, currency
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (restaurant_id, name) DO NOTHING
        """, (
            restaurant_id,
            section,
            item.get("name"),
            item.get("description"),
            item.get("offers", {}).get("price"),
            item.get("offers", {}).get("priceCurrency")
        ))

    def insert_hours(self, restaurant_id, day, open_time, close_time):
        self.cur.execute("""
            INSERT INTO restaurant_hours (restaurant_id, day, opens, closes)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT unique_hours DO NOTHING
        """, (restaurant_id, day, open_time, close_time))


    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()