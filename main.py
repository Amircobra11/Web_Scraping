import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import urljoin

# URL of the site
base_url = 'https://books.toscrape.com/catalogue/page-{}.html'

# Directory to store images
if not os.path.exists('images'):
    os.makedirs('images')

# Function to download image
def download_image(image_url, title):
    # Ensure the image URL is complete
    full_image_url = urljoin('https://books.toscrape.com', image_url)
    img_data = requests.get(full_image_url).content
    img_name = os.path.join('images', f"{title}.jpg")
    with open(img_name, 'wb') as handler:
        handler.write(img_data)

# Function to get books from a specific page
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

# Create CSV file and write header
with open('books.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Price', 'Image URL', 'Book Link'])

    # Loop through the first 5 pages (can adjust as needed)
    for page_num in range(1, 6):
        print(f"Scraping page {page_num}...")
        books = get_books(page_num)

        # Loop through each book and extract details
        for book in books:
            title = book.find('h3').find('a')['title']
            price = book.find('p', class_='price_color').text
            image_url = book.find('img')['src']
            book_link = 'https://books.toscrape.com' + book.find('h3').find('a')['href']

            # Download image
            download_image(image_url, title)

            writer.writerow([title, price, image_url, book_link])
