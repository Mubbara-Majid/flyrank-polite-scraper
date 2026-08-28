import os
import requests

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

if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/page-1.html"
    cache_path = "cache/catalogue-page-1.html"
    fetch_page(url, cache_path)
    fetch_page(url, cache_path)