import os
import zipfile
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import shutil

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

    # Use requests session to reuse connections
    session = requests.Session()

    # Download the main HTML page
    try:
        response = session.get(url)
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

        # Extract resource URLs (CSS, JS, images)
        css_links = [urljoin(url, link.get("href")) for link in soup.find_all("link", {"rel": "stylesheet"})]
        js_links = [urljoin(url, script.get("src")) for script in soup.find_all("script", {"src": True})]
        img_links = [urljoin(url, img.get("src")) for img in soup.find_all("img", {"src": True})]

        # Combine all URLs to download
        all_links = css_links + js_links + img_links

        # Use ThreadPoolExecutor to download resources concurrently
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(download_file, session, link, folder_name): link for link in all_links}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    future.result()  # Wait for the result and handle exceptions if any
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
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
        time.sleep(1)  # Give some time before cleanup to avoid directory not empty error
        shutil.rmtree(folder_name)  # More robust way to remove a directory and its contents
        print(f"Cleaned up folder: {folder_name}")
    except Exception as e:
        print(f"Error cleaning up the folder: {e}")

def download_file(session, url, folder):
    """Download a file and save it in the specified folder with retries."""
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            filename = os.path.basename(urlparse(url).path)
            if filename:
                file_path = os.path.join(folder, filename)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {url}")
        else:
            print(f"Failed to download: {url} - Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        # Retry mechanism for intermittent issues
        retry_download(session, url, folder)

def retry_download(session, url, folder, retries=3, delay=2):
    """Retry downloading with exponential backoff."""
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                filename = os.path.basename(urlparse(url).path)
                if filename:
                    file_path = os.path.join(folder, filename)
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Downloaded (retry): {url}")
                return
        except requests.RequestException as e:
            print(f"Retrying {url}... Attempt {attempt + 1} failed: {e}")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    print(f"Failed to download after {retries} attempts: {url}")

def show_menu():
    print("\n=== Website Downloader ===")
    print("1. Download Website")
    print("2. Exit")
    print("3. List Downloaded Websites")
    print("4. Help")

def list_downloaded_websites():
    print("\n=== Downloaded Websites ===")
    # List folders that are named after domains
    for folder in os.listdir():
        if os.path.isdir(folder) and "_" in folder:
            print(folder)

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == "1":
            url = input("Enter the website URL: ")
            download_website(url)
        elif choice == "2":
            print("Exiting the program...")
            break
        elif choice == "3":
            list_downloaded_websites()
        elif choice == "4":
            print("Help: This program allows you to download a website's HTML, CSS, JS, and images.")
            print("1. Download Website: Input a URL and the website will be downloaded as a .zip file.")
            print("2. Exit: Exit the program.")
            print("3. List Downloaded Websites: List all downloaded websites by their folder name.")
            print("4. Help: Displays this help message.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

