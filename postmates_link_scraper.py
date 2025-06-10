import asyncio
import os
import random
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from db_manager import DatabaseManager
from tasks import scrape_restaurant_task

class PostmatesScraper:
    def __init__(self, address, latitude, longitude, db_manager):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.db = db_manager

    async def scrape(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                geolocation={"latitude": self.latitude, "longitude": self.longitude},
                permissions=["geolocation"],
                locale="en-US"
            )
            page = await context.new_page()
            await page.goto("https://postmates.com/")

            # Handle cookie banner
            try:
                await page.locator("button:has-text('Got it')").click(timeout=3000)
            except:
                pass

            # Dismiss delivery modal if shown
            try:
                await page.locator('button[data-test-id="feed-location-request-modal-dismiss-button"]').click(timeout=5000)
                await asyncio.sleep(random.uniform(1.5, 3.0))
            except:
                pass

            # Fill in the address and hit enter
            await page.wait_for_selector('input[data-testid="location-typeahead-input"]', timeout=8000)
            await page.fill('input[data-testid="location-typeahead-input"]', self.address)
            await asyncio.sleep(2.0)
            await page.keyboard.press("Enter")

            # Wait for the results
            await page.wait_for_selector('a[data-testid="store-card"]', state="attached", timeout=30000)

            # Scroll and click 'Show more'
            while True:
                try:
                    await page.mouse.wheel(0, 5000)
                    await asyncio.sleep(random.uniform(1.5, 3.0))
                    await page.locator("button:has-text('Show more')").click(timeout=3000)
                    await asyncio.sleep(random.uniform(1.5, 3.0))
                except:
                    break

            html = await page.content()
            await browser.close()

        return self.extract_links(html)

    def extract_links(self, html):

        soup = BeautifulSoup(html, "html.parser")
        new_store_links = []
        
        for a in soup.select("a[data-testid='store-card']"):
            href = a.get("href")
            if href and href.startswith("/store/"):
                full_url = f"https://postmates.com{href.split('?')[0]}"
                new_store_links.append((full_url, self.address, 'pending'))


        self.db.insert_store_links(new_store_links)
        self.db.commit()

        for url, address, _ in new_store_links:
            link_id = db.get_link_id_by_url(url)
            status = db.get_link_status(link_id)
            if status == 'pending':
                scrape_restaurant_task.delay(url)

        print(f"📍 {self.address}: Inserted {len(new_store_links)} new links and enqueued for processing.")

# Example usage
if __name__ == "__main__":

    DB_CONFIG = {
        "dbname": "restaurant_data",
        "user": "baileyrusso",
        "host": "localhost",
        "port": "5432"
    }


    db = DatabaseManager(DB_CONFIG)

    locations = [
        {"address": "Madison Square Garden, New York City, New York", "latitude": 40.7505, "longitude": -73.9934},
        # {"address": "Times Square, New York City, New York", "latitude": 40.7580, "longitude": -73.9855},
        # {"address": "Union Square, New York City, New York", "latitude": 40.7359, "longitude": -73.9911},
        # {"address": "World Trade Center, New York City, New York", "latitude": 40.7127, "longitude": -74.0134},
        # {"address": "Harlem, New York City, New York", "latitude": 40.8116, "longitude": -73.9465},

        # # Brooklyn
        # {"address": "Downtown Brooklyn, New York City, New York", "latitude": 40.6928, "longitude": -73.9903},
        # {"address": "Williamsburg, Brooklyn, New York", "latitude": 40.7081, "longitude": -73.9571},
        # {"address": "Coney Island, Brooklyn, New York", "latitude": 40.5749, "longitude": -73.9850},

        # # Queens
        # {"address": "Flushing, Queens, New York", "latitude": 40.7580, "longitude": -73.8303},
        # {"address": "Astoria, Queens, New York", "latitude": 40.7644, "longitude": -73.9235},
        # {"address": "Jamaica, Queens, New York", "latitude": 40.7027, "longitude": -73.7889},

        # # Bronx
        # {"address": "Fordham, Bronx, New York", "latitude": 40.8620, "longitude": -73.8890},
        # {"address": "Riverdale, Bronx, New York", "latitude": 40.9030, "longitude": -73.9126},

        # # Staten Island
        # {"address": "St. George, Staten Island, New York", "latitude": 40.6437, "longitude": -74.0736},
        # {"address": "Tottenville, Staten Island, New York", "latitude": 40.5128, "longitude": -74.2512},
    ]

    async def run_all():
        for loc in locations:
            scraper = PostmatesScraper(loc["address"], loc["latitude"], loc["longitude"], db)
            await scraper.scrape()

    asyncio.run(run_all())

