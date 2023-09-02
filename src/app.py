import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib

# Define command-line arguments
parser = argparse.ArgumentParser(description="Download images from a URL.")
parser.add_argument('url', help='URL to scrape images from')

# Parse the command-line arguments
args = parser.parse_args()
url = args.url

def download_image(img_url, destination_folder):
    img_join = urljoin(url, img_url)
    img_data = requests.get(img_join).content
    img_path = os.path.join(destination_folder, os.path.basename(img_join))
    
    # Calculate the hash of the downloaded image
    img_hash = hashlib.sha256(img_data).hexdigest()

    # Check if the image has already been downloaded
    if not os.path.exists(img_path) or img_hash != get_file_hash(img_path):
        with open(img_path, 'wb') as img_file:
            img_file.write(img_data)
        print(f'Downloaded: {img_path}')
    else:
        print(f'Skipped: {img_path} (already downloaded)')

def get_file_hash(file_path):
    """Calculate the SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(65536)  # Read in 64k chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

# Send an HTTP GET request to the URL
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Create a directory to save the images
destination_folder = 'downloads'
os.makedirs(destination_folder, exist_ok=True)

# Find all image tags in the HTML
img_tags = soup.find_all(['img', 'picture'])

# Download and save each image
for img_tag in img_tags:
    if img_tag.name == 'img':
        img_url = img_tag.get('src')
        if img_url:
            download_image(img_url, destination_folder)
    else:
        # Handle <picture> elements with multiple sources
        source_tags = img_tag.find_all('source')
        for source_tag in source_tags:
            img_url = source_tag.get('srcset')
            if img_url:
                # Extract each source from srcset
                img_urls = [urljoin(url, src.strip()) for src in img_url.split(',')]
                for img_url in img_urls:
                    download_image(img_url, destination_folder)