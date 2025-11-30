from bs4 import BeautifulSoup
from requests import get

class Torrent :
    def find_magnets(content) :
        magnets = set()
        for link in content :
            try :
                resp = get(link, timeout=3)
            except :
                continue
            if "text/html" not in resp.headers.get("content-type", ""):
                continue
            
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a") :
                href = a.get("href")
                if href.startswith("magnet:") :
                    magnets.add(href)
                    print(f"{href}\n")
        return magnets   