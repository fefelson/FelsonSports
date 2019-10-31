from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
from unicodedata import normalize
import json


with open("/home/ededub/pbp.html") as fileIn:
    parser = BeautifulSoup(fileIn, "lxml")
    pbp = []
    for tr in parser.select("#gamepackage-play-by-play tr"):
        try:
            pbp.append((tr.select(".time-stamp")[0].string, tr.select("img")[0]["src"].split("/")[-1].split(".")[0], tr.select(".game-details")[0].string, tr.select(".combined-score")[0].string))
        except IndexError:
            pass

    pprint(pbp)
