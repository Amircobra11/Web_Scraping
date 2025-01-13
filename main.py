import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

base_url = 'https://books.toscrape.com/catalogue/page-{}.html'

if not os.path.exists('images'):
    os.makedirs('images')

conn = sqlite3.connect('books.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS books (
        title TEXT,
        price TEXT,
        image_url TEXT,
        book_link TEXT
    )
''')
conn.commit()


# Function to download image
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


def process_books(books):
    for book in books:
        title = book.find('h3').find('a')['title']
        price = book.find('p', class_='price_color').text
        image_url = book.find('img')['src']
        book_link = 'https://books.toscrape.com' + book.find('h3').find('a')['href']

        download_image(image_url, title)

        c.execute('''
            INSERT INTO books (title, price, image_url, book_link)
            VALUES (?, ?, ?, ?)
        ''', (title, price, image_url, book_link))
        conn.commit()


with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for page_num in range(1, 6):
        futures.append(executor.submit(get_books, page_num))

    for future in as_completed(futures):
        books = future.result()
        if books:
            process_books(books)

conn.close()
