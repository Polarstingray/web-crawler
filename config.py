import argparse
from re import compile

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


def pattern(pattern) :
    pattern = pattern.replace("{d+}", r"(\d+)")
    pattern = pattern.replace("{c+}", r"(.)")
    return pattern


INIT_URL = args.url
PATTERN = compile(pattern(args.pattern))
NUM_WORKERS=5

MAX_DEPTH = 2000
if args.depth :
    try : MAX_DEPTH = int(args.depth)
    except ValueError : print(f"[WARN!] --depth requires an integer value, using default {MAX_DEPTH}.")

IGNORED_QUERY_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign',
    'gclid', 'fbclid', 'ref', 'sessionid', 'category'
}