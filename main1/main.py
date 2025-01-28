import os
import zipfile
import requests
from urllib.parse import urlparse

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

    # Download the main HTML page
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(folder_name, "index.html"), "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Main page downloaded: {url}")
        else:
            print(f"Failed to download the website. Status code: {response.status_code}")
            return
    except Exception as e:
        print(f"Error downloading the website: {e}")
        return

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

# Example usage
download_website("https://ruchitavehale.github.io/ruchitavehale/")

