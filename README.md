# Website Downloader

A Python script to download websites and save them in a ZIP file. The script supports downloading HTML, CSS, JS, and image resources, and it organizes them into folders. Each downloaded website is saved in a unique folder and ZIP file, ensuring that there is no conflict between different websites.

## Features

- **Download Website**: Downloads HTML, CSS, JS, and image files from the provided website URL.
- **Unique Folder/ZIP Naming**: Each website is saved with a unique folder and ZIP file, named in a sequential manner (e.g., `website_1.zip`, `website_2.zip`).
- **Progress Bar**: Displays a progress bar during the download process for each resource.
- **Retry Mechanism**: Handles transient download errors with retries and exponential backoff.
- **Gamified Interface**: Tracks score and level, and displays fun messages when certain milestones are achieved.
- **CLI Interface**: Easy-to-use command-line interface with options to:
  - Download a website.
    - List all previously downloaded websites.
      - Exit the program.
        - Display help.

## Installation

To use this tool, you need to have Python 3.x installed on your system.

1. Clone the repository or download the script:

    ```bash
        git clone https://github.com/your-username/website-downloader.git
        cd website-downloader
    ```

2. Install the required dependencies:

    ```bash
        pip install -r requirements.txt
    ```

This will install the following dependencies:
    - `requests`: To handle HTTP requests and download website content.
    - `beautifulsoup4`: To parse HTML and extract links for CSS, JS, and images.
    - `tqdm`: For the download progress bar.
    - `pyfiglet`: To generate ASCII art headers.
    - `colorama`: For colorful CLI output.

3. Ensure you have Python 3.x installed on your machine (>= 3.6).

## Usage

### Running the Program

Once the dependencies are installed, you can run the program using the following command:
(Run the code in main6/ )

```bash
    python website_downloader.py        #In our case it will be main6.py
```

This will launch the command-line interface with the following options:

1. **Download Website**: You will be prompted to enter a website URL. The website will be downloaded and saved as a ZIP file.
2. **List Downloaded Websites**: Displays all downloaded websites, listed by their folder names (e.g., `website_1`, `website_2`).
3. **Help**: Displays a help message explaining how to use the program.
4. **Exit**: Exit the program.

### Download Website

When you select the option to download a website, the program will:
1. Download the main HTML page.
2. Download associated CSS, JavaScript, and image files.
3. Save the website in a unique folder and ZIP file (e.g., `website_1.zip`).
4. Display a progress bar showing the download status of each resource.

### List Downloaded Websites

This option will list all downloaded websites, showing their folder names (e.g., `website_1`, `website_2`).

### Example Interaction

```bash
=== Website Downloader ===
Level 1 | Score: 20
Successfully Downloaded Files: 3 | Failed Files: 0
1. Download Website
2. Exit
3. List Downloaded Websites
4. Help
Enter your choice (1/2/3/4): 1
Enter the website URL: https://example.com
Main page downloaded: https://example.com
Downloaded: https://example.com/style.css
Downloaded: https://example.com/script.js
Website saved in website_1.zip

=== Website Downloader ===
Level 2 | Score: 40
Successfully Downloaded Files: 4 | Failed Files: 0
1. Download Website
2. Exit
3. List Downloaded Websites
4. Help
```

### File Structure

The program saves downloaded websites in a folder named after the domain (e.g., `website_example_com`) and zips the files into a corresponding `website_1.zip`. The folder structure inside the ZIP is organized as follows:

```
website_1.zip
├── html/
│   └── index.html
├── css/
│   └── style.css
├── js/
│   └── script.js
└── images/
    └── image1.jpg
    ```

### Dependencies

- **requests**: To handle HTTP requests and download files.
- **beautifulsoup4**: To parse HTML and extract URLs for resources.
- **tqdm**: For showing a download progress bar.
- **pyfiglet**: For generating ASCII art headers in the terminal.
- **colorama**: To add colorful output to the terminal.

## License

This project is open source and available under the [MIT License](LICENSE).

---

### Additional Notes:

1. **Directory Structure**: Websites are downloaded into a folder named `website_{domain}` (e.g., `website_example_com`) and saved as a ZIP file.
2. **Error Handling**: The program handles errors such as failed downloads and retries the request up to 3 times with exponential backoff.
3. **Gamification**: The program includes a score and leveling system that increases with each successful download.

---

