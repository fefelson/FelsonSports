from urllib.request import urlopen
from bs4 import BeautifulSoup
from pprint import pprint
import re

league = "mlb"
playerId = 28958

url = "http://www.espn.com/{}/player/_/id/{}".format(league, playerId)
html = urlopen(url)
parser = BeautifulSoup(html, "lxml")

