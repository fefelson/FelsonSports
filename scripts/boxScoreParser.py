from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
from unicodedata import normalize
import json
import re

gameId = 380415102
league = "mlb"

html = {}

url = {
    "summary": "http://www.espn.com/{}/game?gameId={}".format(league, str(gameId)),
    "boxScore": "http://www.espn.com/{}/boxscore?gameId={}".format(league, str(gameId)),
    "teamStats": "http://www.espn.com/{}/matchup?gameId={}".format(league, str(gameId)),
    "playByPlay": "http://www.espn.com/{}/playbyplay?gameId={}".format(league, str(gameId))
    }

for key, item in url.items():
    print("Downloading " + item + "\n")
    html[key] = urlopen(item)

parser = {}
for key, item in html.items():
    parser[key] = BeautifulSoup(item, "lxml")



