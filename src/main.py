import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from urllib.parse import urljoin
from datetime import datetime, timezone
import json

def get_book_cache_path(book_url):
    folder_name = book_url.rstrip("/").split("/")[-2]
    return f"cache/book-{folder_name}.html"


def fetch_page(url, cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"CACHE HIT: {url} - {len(content)} characters.")

            return content

    headers = {
        "User-Agent": "FlyRankInternship/1.0 (+https://github.com/Mubbara-Majid/flyrank-polite-scraper)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    if response.status_code != 200:
        print(f"Error fetching {url}: Status {response.status_code}")
        return None

    response.encoding = "utf-8"
    content = response.text
    print(f"FETCH: {url} - {len(content)} characters.")


    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(response.text)


    return response.text

def get_catalogue_urls(start_url, max_pages=3):
    book_urls = []
    current_url = start_url
    page_num = 1

    
    while current_url and page_num <= max_pages:
        
        cache_path = f"cache/catalogue-page-{page_num}.html"
        was_cached = os.path.exists(cache_path)

        html = fetch_page(current_url, cache_path)
        if html is None:
            break

        if not was_cached:
            time.sleep(0.5)   

        soup = BeautifulSoup(html, "html.parser")

        links = soup.select("article.product_pod h3 a")
        for link in links:
            absolute = urljoin(current_url, link["href"])
            book_urls.append((absolute, current_url))

        next_link = soup.select_one("li.next a")
        if next_link:
            current_url = urljoin(current_url, next_link["href"])
        else:
            current_url = None

        page_num += 1

    return list(dict.fromkeys(book_urls))



def extract_book(book_url, source_page):
    cache_path = get_book_cache_path(book_url)
    html = fetch_page(book_url, cache_path)
    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("h1").text
    price_text = soup.select_one("p.price_color").text
    availability_text = soup.select_one("p.instock.availability").text
    rating_text = soup.select_one("p.star-rating")["class"][1]

    desc_heading = soup.select_one("#product_description")
    if desc_heading:
        description = desc_heading.find_next_sibling("p").text
    else:
        description = None

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }

if __name__ == "__main__":
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    
    # 1. Discover all URLs (Stage 2)
    print("--- Starting URL Discovery ---")
    book_urls = get_catalogue_urls(start_url)
    print(f"catalogue_pages = 3, discovered = {len(book_urls)}, unique_urls = {len(set(book_urls))}")

    # 2. Extract records (Stage 3)
    print("\n--- Starting Extraction ---")
    records = []
    
    for book_url, source_page in book_urls:
        cache_path = get_book_cache_path(book_url)
        was_cached = os.path.exists(cache_path)

        record = extract_book(book_url, source_page)
        if record:
            records.append(record)

        if not was_cached:
            time.sleep(0.5)


    print("\n--- Stage 3 Checkpoint ---")
    if records:
        print(json.dumps(records[0], indent=2))
    
    print(f"\ndetail_pages = {len(records)}")