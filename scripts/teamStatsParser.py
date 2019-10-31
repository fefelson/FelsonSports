from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
from unicodedata import normalize
import json


with open("/home/ededub/teamStats.html") as fileIn:
    parser = BeautifulSoup(fileIn, "lxml")
##    for tr in parser.select("article tr"):
##        if "data-stat-attr" in tr.attrs.keys():
##            print(tr["data-stat-attr"], tr.select("td")[1].string.strip())
##
##


    pprint(dict(zip([tr["data-stat-attr"] for tr in parser.select("article tr") if "data-stat-attr" in tr.attrs.keys()], [tr.select("td")[1].string.strip()  for tr in parser.select("article tr") if "data-stat-attr" in tr.attrs.keys()])))
