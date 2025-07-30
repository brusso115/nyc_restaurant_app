import psycopg2
import os

class RestaurantAPIData:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cur = self.conn.cursor()

    def fetch_all_restaurants(self):
        self.cur.execute("""
            SELECT r.id, r.name, r.latitude, r.longitude, c.name
            FROM restaurants r
            JOIN restaurant_categories rc ON r.id = rc.restaurant_id
            JOIN categories c ON rc.category_id = c.id
            WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL
        """)
        rows = self.cur.fetchall()

        restaurants = {}
        for r_id, name, lat, lng, category in rows:
            if r_id not in restaurants:
                restaurants[r_id] = {
                    "id": r_id,
                    "name": name,
                    "latitude": lat,
                    "longitude": lng,
                    "categories": []
                }
            restaurants[r_id]["categories"].append(category)

        return list(restaurants.values())
    
    def fetch_all_categories(self):
        self.cur.execute("SELECT name FROM categories ORDER BY name")
        rows = self.cur.fetchall()
        return [{"name": row[0]} for row in rows]

    def close(self):
        self.cur.close()
        self.conn.close()