import re
import os
import requests
from urllib.parse import urljoin, urlparse

# Config
INPUT_FILE = "urls.txt"
FILE_EXTENSIONS = (".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".rar", ".txt", ".csv")
BASE_FOLDER = "SQAPapers"

# Make base folder
os.makedirs(BASE_FOLDER, exist_ok=True)

# Load URL list
with open(INPUT_FILE, "r") as f:
    entries = [line.strip() for line in f if line.strip()]

for entry in entries:
    if '|' not in entry:
        print(f"Skipping malformed line: {entry}")
        continue

    year, url = entry.split('|', 1)
    year_folder = os.path.join(BASE_FOLDER, year)
    os.makedirs(year_folder, exist_ok=True)

    try:
        response = requests.get(url)
        html = response.text
        print(f"\n[+] Scanning {url} for year {year}")
        links = re.findall(r'href=["\'](.*?)["\']', html)

        for href in links:
            if any(href.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                file_url = urljoin(url, href)
                filename = os.path.basename(urlparse(file_url).path)
                filepath = os.path.join(year_folder, filename)

                if os.path.exists(filepath):
                    print(f"Already exists: {filename}")
                    continue

                try:
                    with requests.get(file_url, stream=True) as r:
                        r.raise_for_status()
                        with open(filepath, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Failed to download {file_url}: {e}")

    except Exception as e:
        print(f"Failed to process {url}: {e}")
