import os
import zipfile
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import shutil
from tqdm import tqdm
import pyfiglet
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Global variables for scoring and level tracking
score = 0
level = 1
downloaded_files = 0
failed_files = 0

def update_score(success=True):
    global score, downloaded_files, failed_files
    if success:
        score += 10  # Each successful download adds 10 points
        downloaded_files += 1
    else:
        failed_files += 1
    # Level up after every 5 successful downloads
    if downloaded_files // 5 >= level:
        level_up()

def level_up():
    global level
    level += 1
    print(Fore.GREEN + f"🎉 Congratulations! You've reached Level {level}! 🎉")

def download_website(url, zip_name="website.zip"):
    global score, level, downloaded_files, failed_files

    # Graffiti-like header for the download
    print(Fore.YELLOW + pyfiglet.figlet_format("Downloading Website", font="slant"))
    print(Fore.CYAN + f"Attempting to download: {url}")

    # Parse the URL to get the base URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if not domain:
        print(Fore.RED + "Invalid URL")
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
            print(Fore.GREEN + f"Main page downloaded: {url}")
            update_score(True)
        else:
            print(Fore.RED + f"Failed to download the website. Status code: {response.status_code}")
            update_score(False)
            return
    except Exception as e:
        print(Fore.RED + f"Error downloading the website: {e}")
        update_score(False)
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

        # Use ThreadPoolExecutor to download resources concurrently with a progress bar
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(download_file, session, link, folder_name): link for link in all_links}
            with tqdm(total=len(futures), desc="Downloading resources", unit="file", ncols=100) as pbar:
                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        future.result()  # Wait for the result and handle exceptions if any
                        update_score(True)
                    except Exception as e:
                        print(Fore.RED + f"Error downloading {url}: {e}")
                        update_score(False)
                    pbar.update(1)
    except Exception as e:
        print(Fore.RED + f"Error parsing HTML and downloading resources: {e}")
        update_score(False)

    # Zip the folder into a .zip file with correct folder structure
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_name):
                for file in files:
                    # Preserve the folder structure when adding to zip
                    file_path = os.path.join(root, file)
                    # Get the relative path to add to the zip file
                    arcname = os.path.relpath(file_path, folder_name)
                    zipf.write(file_path, arcname=arcname)
        print(Fore.GREEN + f"Website saved in {zip_name}")
        update_score(True)
    except Exception as e:
        print(Fore.RED + f"Error creating ZIP file: {e}")
        update_score(False)

    # Optionally, remove the downloaded files after zipping
    try:
        time.sleep(1)  # Give some time before cleanup to avoid directory not empty error
        shutil.rmtree(folder_name)  # More robust way to remove a directory and its contents
        print(Fore.YELLOW + f"Cleaned up folder: {folder_name}")
    except Exception as e:
        print(Fore.RED + f"Error cleaning up the folder: {e}")

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
                print(Fore.GREEN + f"Downloaded: {url}")
            update_score(True)
        else:
            print(Fore.RED + f"Failed to download: {url} - Status code: {response.status_code}")
            update_score(False)
    except requests.RequestException as e:
        print(Fore.RED + f"Error downloading {url}: {e}")
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
                    print(Fore.GREEN + f"Downloaded (retry): {url}")
                update_score(True)
                return
        except requests.RequestException as e:
            print(Fore.YELLOW + f"Retrying {url}... Attempt {attempt + 1} failed: {e}")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    print(Fore.RED + f"Failed to download after {retries} attempts: {url}")
    update_score(False)

def show_menu():
    print(Fore.MAGENTA + pyfiglet.figlet_format("Website Downloader", font="slant"))
    print(Fore.YELLOW + f"Level {level} | Score: {score}")
    print(Fore.YELLOW + f"Successfully Downloaded Files: {downloaded_files} | Failed Files: {failed_files}")
    print(Fore.CYAN + "1. Download Website")
    print(Fore.CYAN + "2. Exit")
    print(Fore.CYAN + "3. List Downloaded Websites")
    print(Fore.CYAN + "4. Help")

def list_downloaded_websites():
    print(Fore.GREEN + "\n=== Downloaded Websites ===")
    # List folders that are named after domains
    for folder in os.listdir():
        if os.path.isdir(folder) and "_" in folder:
            print(Fore.BLUE + folder)

def main():
    while True:
        show_menu()
        choice = input(Fore.CYAN + "Enter your choice (1/2/3/4): ")

        if choice == "1":
            url = input(Fore.CYAN + "Enter the website URL: ")
            download_website(url)
        elif choice == "2":
            print(Fore.RED + "Exiting the program...")
            break
        elif choice == "3":
            list_downloaded_websites()
        elif choice == "4":
            print(Fore.GREEN + "Help: This program allows you to download a website's HTML, CSS, JS, and images.")
            print(Fore.GREEN + "1. Download Website: Input a URL and the website will be downloaded as a .zip file.")
            print(Fore.GREEN + "2. Exit: Exit the program.")
            print(Fore.GREEN + "3. List Downloaded Websites: List all downloaded websites by their folder name.")
            print(Fore.GREEN + "4. Help: Displays this help message.")
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

