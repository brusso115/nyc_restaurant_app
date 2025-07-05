import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

import asyncio
import random
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from common.db_manager import DatabaseManager
from playwright.async_api import Page
from celery import Celery

celery = Celery("scraper")
celery.config_from_envvar("CELERY_CONFIG_MODULE", silent=True)  # Optional fallback
celery.conf.update(
    broker_url=os.environ.get("CELERY_BROKER_URL"),
    result_backend=os.environ.get("CELERY_RESULT_BACKEND"),
    task_serializer=os.environ.get("CELERY_TASK_SERIALIZER", "json"),
    accept_content=eval(os.environ.get("CELERY_ACCEPT_CONTENT", '["json"]')),
    timezone=os.environ.get("CELERY_TIMEZONE", "UTC"),
    enable_utc=os.environ.get("CELERY_ENABLE_UTC", "True") == "True"
)

class PostmatesScraper:

    def __init__(self, address, latitude, longitude, db_manager):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.db = db_manager

    async def handle_cookie_banner(self, page: Page):
        try:
            await page.locator("button:has-text('Got it')").click(timeout=3000)
        except:
            pass

    async def dismiss_delivery_modal(self, page: Page):
        try:
            await page.locator(
                'button[data-test-id="feed-location-request-modal-dismiss-button"]'
            ).click(timeout=5000)
            await asyncio.sleep(random.uniform(1.5, 3.0))
        except:
            pass

    async def enter_address(self, page: Page):
        await page.wait_for_selector(
            'input[data-testid="location-typeahead-input"]', timeout=8000
        )
        await page.fill('input[data-testid="location-typeahead-input"]', self.address)
        await asyncio.sleep(2.0)
        await page.keyboard.press("Enter")

    async def wait_for_results(self, page: Page):
        await page.wait_for_selector(
            'a[data-testid="store-card"]', state="attached", timeout=30000
        )

    async def scroll_and_click_show_more(self, page: Page):
        while True:
            try:
                await page.mouse.wheel(0, 5000)
                await asyncio.sleep(random.uniform(1.5, 3.0))
                await page.locator("button:has-text('Show more')").click(timeout=3000)
                await asyncio.sleep(random.uniform(1.5, 3.0))
            except:
                break

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
            link_id = self.db.get_link_id_by_url(url)
            status = self.db.get_link_status(link_id)
            if status in ('pending'):
                try:
                    result = celery.send_task("scraper_worker.tasks.scrape_restaurant_task", args=[url], queue="scraper_queue")
                    print(f"📨 Task sent for: {url}, task_id={result.id}")
                except Exception as e:
                    print(f"❌ Failed to enqueue {url}: {e}")

        print(f"📍 {self.address}: Inserted {len(new_store_links)} new links and enqueued for processing.")

    async def scrape(self):
        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=False)

            try:
                context = await browser.new_context(
                    geolocation={"latitude": self.latitude, "longitude": self.longitude},
                    permissions=["geolocation"],
                    locale="en-US"
                )
                page = await context.new_page()
                await page.goto("https://postmates.com/")

                await self.handle_cookie_banner(page)
                await self.dismiss_delivery_modal(page)
                await self.enter_address(page)
                await self.wait_for_results(page)
                await self.scroll_and_click_show_more(page)

                html = await page.content()
            finally:
                await browser.close()

        self.extract_links(html)

# Example usage
if __name__ == "__main__":

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

