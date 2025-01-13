import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# URL of the site
base_url = 'https://books.toscrape.com/catalogue/page-{}.html'

# Directory to store images
if not os.path.exists('images'):
    os.makedirs('images')

# Create a list to store book data
books_data = []

# Function to download image
def download_image(image_url, title):
    try:
        # Ensure the image URL is complete
        full_image_url = urljoin('https://books.toscrape.com', image_url)
        img_data = requests.get(full_image_url, timeout=10).content
        img_name = os.path.join('images', f"{title}.jpg")
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        print(f"Image downloaded: {title}")
        return img_name
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {title}: {e}")
        return None

# Function to get books from a specific page
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

# Function to process books and store in books_data
def process_books(books):
    for book in books:
        title = book.find('h3').find('a')['title']
        price = book.find('p', class_='price_color').text
        image_url = book.find('img')['src']
        book_link = 'https://books.toscrape.com' + book.find('h3').find('a')['href']

        # Download image and get image path
        image_path = download_image(image_url, title)

        # Store book data in books_data list
        books_data.append({
            'title': title,
            'price': price,
            'image_url': image_url,
            'image_path': image_path,  # Store the local image path
            'book_link': book_link
        })

# Create a ThreadPoolExecutor for parallel requests
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    # Loop through the first 5 pages (can adjust as needed)
    for page_num in range(1, 2):
        futures.append(executor.submit(get_books, page_num))

    for future in as_completed(futures):
        books = future.result()
        if books:
            process_books(books)

# Save the books data to a JSON file
with open('books_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(books_data, json_file, ensure_ascii=False, indent=4)

# Generate HTML table to display the data with images
html_content = '''
<html>
<head>
    <title>Books Scraped</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        h1 {
            text-align: center;
            color: #333;
            padding: 20px;
            background-color: #333;
            color: white;
        }
        table {
            width: 80%;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: #fff;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #333;
            color: white;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        a {
            color: #333;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            color: #0066cc;
        }
        img {
            width: 100px;
            height: 150px;
            object-fit: cover;
        }
    </style>
</head>
<body>
    <h1>Books List</h1>
    <table>
        <tr><th>Image</th><th>Title</th><th>Price</th><th>Link</th></tr>
'''

for book in books_data:
    image_tag = f'<img src="{book["image_path"]}" alt="{book["title"]}"/>' if book['image_path'] else 'No Image'
    html_content += f'<tr><td>{image_tag}</td><td>{book["title"]}</td><td>{book["price"]}</td><td><a href="{book["book_link"]}" target="_blank">View Book</a></td></tr>'

html_content += '</table></body></html>'

# Save the HTML content to a file
with open('books_data_with_images.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

print("Data saved to books_data.json and books_data_with_images.html")
