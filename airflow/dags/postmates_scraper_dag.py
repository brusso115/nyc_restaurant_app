import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

import sys
import time
import asyncio
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from airflow import DAG
from airflow.operators.python import PythonOperator
from common.db_manager import DatabaseManager
from scraper.postmates_link_scraper import PostmatesScraper  # adjust path if needed

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Locations to scrape (in order)
locations = [
    {"address": "Madison Square Garden, NYC", "latitude": 40.7505, "longitude": -73.9934},
    {"address": "Times Square, NYC", "latitude": 40.7580, "longitude": -73.9855},
    {"address": "Union Square, NYC", "latitude": 40.7359, "longitude": -73.9911},
    {"address": "World Trade Center, New York City, New York", "latitude": 40.7127, "longitude": -74.0134},
    {"address": "Harlem, New York City, New York", "latitude": 40.8116, "longitude": -73.9465},
    {"address": "Downtown Brooklyn, New York City, New York", "latitude": 40.6928, "longitude": -73.9903},
    {"address": "Williamsburg, Brooklyn, New York", "latitude": 40.7081, "longitude": -73.9571},
    {"address": "Coney Island, Brooklyn, New York", "latitude": 40.5749, "longitude": -73.9850},
    {"address": "Flushing, Queens, New York", "latitude": 40.7580, "longitude": -73.8303},
    {"address": "Astoria, Queens, New York", "latitude": 40.7644, "longitude": -73.9235},
    {"address": "Jamaica, Queens, New York", "latitude": 40.7027, "longitude": -73.7889},
    {"address": "Fordham, Bronx, New York", "latitude": 40.8620, "longitude": -73.8890},
    {"address": "Riverdale, Bronx, New York", "latitude": 40.9030, "longitude": -73.9126},
    {"address": "St. George, Staten Island, New York", "latitude": 40.6437, "longitude": -74.0736},
    {"address": "Tottenville, Staten Island, New York", "latitude": 40.5128, "longitude": -74.2512},
]

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="postmates_scraper_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
)

def scrape_location(location):
    db = DatabaseManager(DB_CONFIG)
    scraper = PostmatesScraper(location["address"], location["latitude"], location["longitude"], db)
    asyncio.run(scraper.scrape())

def wait_one_hour():
    time.sleep(1800)

previous_scrape = None
for i, loc in enumerate(locations):
    scrape = PythonOperator(
        task_id=f"scrape_{loc['address'].replace(' ', '_').replace(',', '').lower()}",
        python_callable=scrape_location,
        op_args=[loc],
        dag=dag
    )

    if previous_scrape:
        wait = PythonOperator(
            task_id=f"wait_after_scrape_{i-1}",
            python_callable=wait_one_hour,
            dag=dag
        )
        previous_scrape >> wait >> scrape
    previous_scrape = scrape
