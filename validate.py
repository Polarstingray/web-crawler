from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from config import IGNORED_QUERY_PARAMS


class Validation :
    def normalize(url) :
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc.lower()

        if (scheme == "http") and netloc.endswith(":80") : netloc = netloc[:-3]
        elif (scheme == "https") and netloc.endswith(":443") : netloc = netloc[:-4]

        path = parsed_url.path.rstrip('/') 
        query_pairs = parse_qsl(parsed_url.query, keep_blank_values=True)
        filtered = [
            (k, v)
            for k, v in query_pairs
            if k not in IGNORED_QUERY_PARAMS
        ]
        filtered.sort()
        query = urlencode(filtered)
        return urlunparse((scheme, netloc, path, "", query, ""))
