
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re
import argparse

parser = argparse.ArgumentParser(
    prog="charlotte",
    description="web-crawler that recursively searches for patterns on a domain."
)   

parser.add_argument("url", help="base url where search begins")
parser.add_argument("-p", "--pattern", help="regex pattern to search for", required=True)
parser.add_argument('-v', '--verbose', action='store_true')

args = parser.parse_args()


INIT_URL = args.url
PATTERN = re.compile(args.pattern.replace("d+", r"(\d+)"))
visited = set()
matches = []

print(INIT_URL)

def crawl(url) :
    if url in visited :
        return 
    
    visited.add(url)
    if args.verbose :
        print(f'crawling: {url}')
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
        
        if args.verbose :
            print(abs_url)

        if PATTERN.search(abs_url) and abs_url not in matches: 
            matches.append(abs_url)
            print("MATCH: "+abs_url)
        if abs_url.startswith(INIT_URL) :
            crawl(abs_url)        

print(f"starting web at {INIT_URL}")
crawl(INIT_URL)

if args.verbose :
    for match in matches :
        print(match)
print(f'Found {len(matches)} matches!')