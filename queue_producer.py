from tasks import scrape_restaurant_task

def enqueue_store_link(url):
    scrape_restaurant_task.delay(url)