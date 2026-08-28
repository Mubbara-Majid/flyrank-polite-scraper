import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from urllib.parse import urljoin

page_url = "https://books.toscrape.com/catalogue/page-1.html"

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
            book_urls.append(absolute)

        next_link = soup.select_one("li.next a")
        if next_link:
            current_url = urljoin(current_url, next_link["href"])
        else:
            current_url = None

        page_num += 1

    return list(dict.fromkeys(book_urls))

if __name__ == "__main__":
    urls = get_catalogue_urls("https://books.toscrape.com/catalogue/page-1.html", max_pages=3)
    print(f"catalogue_pages=3 discovered={len(urls)} unique_urls={len(set(urls))}")