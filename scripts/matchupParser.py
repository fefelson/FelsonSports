from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
from unicodedata import normalize
import json


html = urlopen("http://www.espn.com/nba/game?gameId=400975640")

parser = BeautifulSoup(html, "lxml")
