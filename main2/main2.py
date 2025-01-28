import os
import zipfile
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def download_website(url, zip_name="website.zip"):
    # Parse the URL to get the base URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if not domain:
        print("Invalid URL")
        return

    # Create a folder to save the website's files
    folder_name = domain.replace(".", "_")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Create folders for different file types
    os.makedirs(os.path.join(folder_name, "html"), exist_ok=True)
    os.makedirs(os.path.join(folder_name, "css"), exist_ok=True)
    os.makedirs(os.path.join(folder_name, "js"), exist_ok=True)
    os.makedirs(os.path.join(folder_name, "images"), exist_ok=True)

    # Download the main HTML page
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_path = os.path.join(folder_name, "html", "index.html")
            with open(html_path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Main page downloaded: {url}")
        else:
            print(f"Failed to download the website. Status code: {response.status_code}")
            return
    except Exception as e:
        print(f"Error downloading the website: {e}")
        return

    # Parse HTML and download linked resources (CSS, JS, images)
    try:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Download all CSS files
        css_links = soup.find_all("link", {"rel": "stylesheet"})
        for link in css_links:
            href = link.get("href")
            if href:
                css_url = urljoin(url, href)
                download_file(css_url, os.path.join(folder_name, "css"))

        # Download all JS files
        js_scripts = soup.find_all("script", {"src": True})
        for script in js_scripts:
            src = script.get("src")
            if src:
                js_url = urljoin(url, src)
                download_file(js_url, os.path.join(folder_name, "js"))

        # Download images (img tags)
        img_tags = soup.find_all("img", {"src": True})
        for img in img_tags:
            src = img.get("src")
            if src:
                img_url = urljoin(url, src)
                download_file(img_url, os.path.join(folder_name, "images"))
    except Exception as e:
        print(f"Error parsing HTML and downloading resources: {e}")

    # Zip the folder into a .zip file
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_name):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), folder_name))
        print(f"Website saved in {zip_name}")
    except Exception as e:
        print(f"Error creating ZIP file: {e}")

    # Optionally, remove the downloaded files after zipping
    try:
        for root, _, files in os.walk(folder_name, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(folder_name)
    except Exception as e:
        print(f"Error cleaning up the folder: {e}")

def download_file(url, folder):
    """Download a file and save it in the specified folder."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.basename(urlparse(url).path)
            if filename:
                file_path = os.path.join(folder, filename)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {url}")
        else:
            print(f"Failed to download: {url} - Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Example usage
download_website("https://ruchitavehale.github.io/ruchitavehale/")

