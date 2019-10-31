from urllib.request import urlopen, Request
from pprint import pprint
import gzip

url = "https://s.yimg.com/aaq/yc/2.8.0/en.js"

x =urlopen(url)
pprint(gzip.decompress(x.read()))
