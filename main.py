import requests
from bs4 import BeautifulSoup

URL = "https://example.com/products"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    else:
        print(f"خطا در دریافت صفحه: {response.status_code}")
        return None

if __name__ == "__main__":
    html = fetch_page(URL)
    if html:
        print("صفحه با موفقیت دریافت شد!")
