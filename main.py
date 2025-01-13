import requests
from bs4 import BeautifulSoup
import csv

base_url = 'https://books.toscrape.com/catalogue/page-{}.html'

def get_books(page_num):
    url = base_url.format(page_num)
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        return books
    else:
        print(f"Failed to retrieve page {page_num}.")
        return []

with open('books.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Price', 'Image URL'])

    for page_num in range(1, 2):
        print(f"Scraping page {page_num}...")
        books = get_books(page_num)

        for book in books:
            title = book.find('h3').find('a')['title']
            price = book.find('p', class_='price_color').text
            image_url = book.find('img')['src']
            writer.writerow([title, price, image_url])
