
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re

INIT_URL = "https://eztvx.to"
PATTERN = re.compile(r"package-V(\d+\.\d+)")
visited = set()
matches = []


def crawl(url) :
    if url in visited :
        return
    
    visited.add(url)
    try :
        resp = requests.get(url, timeout=3)
    except :
        return

    if "text/html" not in resp.headers.get("content-type", ""):
        return
    
    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.find_all("a") :
        href = a.get('href')
        if not href :
            continue
    
        abs_url = urljoin(url, href)

        if PATTERN.search(abs_url) : 
            matches.append(abs_url)
            print("MATCH: "+abs_url)
        if abs_url.startswith(INIT_URL) :
            crawl(abs_url)

crawl(INIT_URL)