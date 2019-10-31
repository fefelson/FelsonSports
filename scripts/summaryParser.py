from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
from unicodedata import normalize
import json
import re


with open("/home/ededub/summary.html") as fileIn:
    parser = BeautifulSoup(fileIn, "lxml")
    matchup = parser.select("#custom-nav .competitors")[0]
    info = parser.select("#gamepackage-game-information article .content")[0]

    
    #print(matchup)
    #print("\n\n\n")
    print(info)
        
    
