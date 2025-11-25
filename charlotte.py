
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
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
parser.add_argument('-t', '--torrent', action='store_true', help="find magnet links from each matched url")
parser.add_argument('-d', '--depth', help='specifies maximum depth')

args = parser.parse_args()


INIT_URL = args.url
PATTERN = re.compile(args.pattern.replace("d+", r"(\d+)"))
visited = set()

# global set of matches, shouldn't have duplicates by its construction
matches = []
MAX_DEPTH = 2000
if args.depth :
    try :
        MAX_DEPTH = int(args.depth)
    except ValueError :
        print(f"[WARN!] --depth requires an integer value, using default {MAX_DEPTH}.")


IGNORED_QUERY_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign',
    'gclid', 'fbclid', 'ref', 'sessionid'
}

def normalize(url) :
    parsed_url = urlparse(url)

    scheme = parsed_url.scheme

    netloc = parsed_url.netloc.lower()

    if (scheme == "http") and netloc.endswith(":80") :
        netloc = netloc[:-3]
    elif (scheme == "https") and netloc.endswith(":443") :
        netloc = netloc[:-4]

    path = parsed_url.path.rstrip('/') 

    query_pairs = parse_qsl(parsed_url.query, keep_blank_values=True)

    filtered = [
        (k, v)
        for k, v in query_pairs
        if k not in IGNORED_QUERY_PARAMS
    ]

    # Sort alphabetically
    filtered.sort()

    query = urlencode(filtered)
    
    return urlunparse((scheme, netloc, path, "", query, ""))


def crawl(url, depth=0, limit=MAX_DEPTH) :
    url = normalize(url)
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
            if (depth >= limit) :
                continue
            depth += 1
            crawl(abs_url, depth)        

def torrent(content) :
    magnets = set()
    for link in content :
        try :
            resp = requests.get(link, timeout=3)
        except :
            continue
        if "text/html" not in resp.headers.get("content-type", ""):
            break
        
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a") :
            href = a.get("href")
            if href.startswith("magnet:") :
                magnets.add(href)
                print(f"{href}\n")
    return magnets    


if __name__ == "__main__" :
    print(f"starting web at {INIT_URL}")
    crawl(INIT_URL)
    
    if args.verbose :
        for match in matches :
            print(f"MATCH: {match}")
    print(f'Found {len(matches)} matches!')

    if args.torrent :
        magnets = torrent(matches)
        print(f"Found {len(magnets)} torrents!")
