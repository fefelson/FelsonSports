from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
from pprint import pprint

url = "http://www.espn.com/mlb/team/_/name/chw/chicago-white-sox"
html = urlopen(url)
parser = BeautifulSoup(html, "lxml")

