import psycopg2
import os

class RestaurantAPIData:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cur = self.conn.cursor()

    def fetch_all_restaurants(self):
        self.cur.execute("""
            SELECT id, name, latitude, longitude
            FROM restaurants
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        rows = self.cur.fetchall()
        return [
            {"id": r[0], "name": r[1], "latitude": r[2], "longitude": r[3]}
            for r in rows
        ]

    def close(self):
        self.cur.close()
        self.conn.close()