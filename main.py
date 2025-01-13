import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = 'https://books.toscrape.com/catalogue/page-{}.html'

if not os.path.exists('images'):
    os.makedirs('images')

def download_image(image_url, title):
    try:
        full_image_url = urljoin('https://books.toscrape.com', image_url)
        img_data = requests.get(full_image_url, timeout=10).content
        img_name = os.path.join('images', f"{title}.jpg")
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        print(f"Image downloaded: {title}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {title}: {e}")

def get_books(page_num):
    url = base_url.format(page_num)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        return books
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page {page_num}: {e}")
        return []

def process_books(books, writer):
    for book in books:
        title = book.find('h3').find('a')['title']
        price = book.find('p', class_='price_color').text
        image_url = book.find('img')['src']
        book_link = 'https://books.toscrape.com' + book.find('h3').find('a')['href']

        download_image(image_url, title)

        writer.writerow([title, price, image_url, book_link])

with open('books.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Price', 'Image URL', 'Book Link'])

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for page_num in range(1, 6):
            futures.append(executor.submit(get_books, page_num))

        for future in as_completed(futures):
            books = future.result()
            if books:
                process_books(books, writer)
