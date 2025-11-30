
from time import sleep
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

from torrent import Torrent
import config
from config import args
from validate import Validation

# global set of matches, shouldn't have duplicates by its construction
matches = []
visited = set()

def crawl(url=config.INIT_URL, visited=visited, matches=matches, limit=config.MAX_DEPTH) :
    lock = threading.Lock()
    tasks = queue.Queue()
    url = Validation.normalize(url)
    tasks.put((url, 0))
    with lock :
        visited.add(url)
    futures = []
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor :
        for _ in range(config.NUM_WORKERS) :
            futures.append(executor.submit(worker, tasks, limit, visited, matches, lock))
        tasks.join()
    return

def worker(tasks, limit, visited, matches, lock) :
    while True :
        try :
            url, depth = tasks.get(timeout=1)
            if (args.verbose) : print("getting task", flush=True), print(f"depth: {depth}")
        except queue.Empty:
            return
        
        sub_pages = process_page(Validation.normalize(url), matches, lock)
        if sub_pages and depth < limit :
            for url in sub_pages :
                if depth + 1 <= limit :
                    with lock :
                        if url not in visited :
                            if (args.verbose) : print(f"{url} - adding task") 
                            visited.add(url)
                            tasks.put((url, depth + 1))
                        elif (args.verbose) : print(f"{url} - already visited")
        tasks.task_done()

def process_page(url, matches, lock) :
    if args.verbose : 
        print(f'crawling: {url}', flush=True) 
        print("getting site...")

    try : resp = requests.get(url, timeout=3)
    except Exception as e: 
        print(f"[WARN/ERR] {str(e)}")
        return False

    if "text/html" not in resp.headers.get("content-type", ""):
        return False
        
    soup = BeautifulSoup(resp.text, "html.parser")
    if args.verbose : print("parsing page...")
    sub_pages = []
    for a in soup.find_all("a") :
        href = a.get('href')
        if not href :
            continue
        abs_url = Validation.normalize(urljoin(url, href))
        if args.verbose : print(abs_url)
        if config.PATTERN.search(abs_url) and abs_url: 
            with lock :
                matches.append(abs_url)
                print("MATCH: "+abs_url, flush=True)
        elif abs_url.startswith(config.INIT_URL) :
            sub_pages.append(abs_url)
    return sub_pages



def rec_crawl(url, depth=0, limit=config.MAX_DEPTH) :
    url = Validation.normalize(url)
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

        if config.PATTERN.search(abs_url) and abs_url not in matches: 
            matches.append(abs_url)
            print("MATCH: "+abs_url)

        if abs_url.startswith(config.INIT_URL) :
            if (depth >= limit) :
                continue
            depth += 1
            rec_crawl(abs_url, depth) 
 


if __name__ == "__main__" :
    start_time = time.perf_counter()

    print(f"starting web at {config.INIT_URL}")
    crawl(config.INIT_URL) 

    depth = len(visited)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    if args.verbose :
        for match in matches :
            print(f"MATCH: {match}")
        print(f"took {elapsed_time} seconds")
    print(f'Found {len(matches)} matches!')


    if args.torrent :
        magnets = Torrent.find_magnets(matches)
        print(f"Found {len(magnets)} torrents!")
