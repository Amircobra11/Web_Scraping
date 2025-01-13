import requests
from bs4 import BeautifulSoup
import csv

# URL of the site
url = 'https://books.toscrape.com/'

# Send request to the site
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all books on the page
    books = soup.find_all('article', class_='product_pod')

    # Create CSV file and write data
    with open('books.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Image URL'])

        # Loop through each book and extract details
        for book in books:
            title = book.find('h3').find('a')['title']
            price = book.find('p', class_='price_color').text
            image_url = book.find('img')['src']
            writer.writerow([title, price, image_url])
else:
    print("Failed to retrieve the webpage.")
