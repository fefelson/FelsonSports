from os import environ
from pprint import pprint
from bs4 import BeautifulSoup
from SportsDB.WebService.ESPN.PlayerParser import normal




mainPath = environ["HOME"] +"/Downloads/{}.html"

kept2017 = []
kept2018 = []

players = {}
espnValues = {}

with open(mainPath.format("espnvalues"))as fileIn:
    info = fileIn.read()

parser = BeautifulSoup(info, "lxml")
for tr in parser.select("aside table tbody tr"):
    name = normal(tr.select("a")[0].string)
    price = tr.select("td")[-2].string
    espnValues[name] = price






with open(mainPath.format("2017_draft")) as fileIn:

    info = fileIn.read()

parser = BeautifulSoup(info, "lxml")
for player in parser.select(".F-icon"):
    mainElement = player.parent.parent
    kept2017.append(mainElement.a["href"].split("/")[-1])



with open(mainPath.format("2018_draft")) as fileIn:

    info = fileIn.read()

parser = BeautifulSoup(info, "lxml")
for player in parser.select(".F-icon"):
    mainElement = player.parent.parent
    kept2018.append(mainElement.a["href"].split("/")[-1])

for player in parser.select(".player"):
    playerId = player.a["href"].split("/")[-1]
    name = player.a.string
    mainElement = player.parent
    cost = int(mainElement.select(".cost")[0].string.split("$")[1])
    players[playerId] = {"name":name,"cost":cost+5}

cantKeep = set(kept2017) & set(kept2018)

pprint([players[playerId]["name"] for playerId in cantKeep])


for fileName in ("felsons", "konk", "wootenhaad", "pc", "lilmoe", "jerzy", "caddillac",
                  "beantown", "51s", "generals"):

    with open(mainPath.format(fileName)) as fileIn:
              info = fileIn.read()

    parser = BeautifulSoup(info, "lxml")
    print("\n\n\n")
    print(fileName.capitalize())
    print()
    
    for player in parser.select(".name"):
        playerId = player["href"].split("/")[-1]
        name = normal(player.string)
        if playerId not in cantKeep:
            p = players.get(playerId, {"name":name, "cost":"espn"})
            try:
                print(p["name"], "\tdraft+5  $"+str(p["cost"]),"\tespn  "+espnValues[name], "\n")
            except KeyError:
                print(p["name"], "\tdraft+5  $"+str(p["cost"]),"\tToo Lazy to figure it out", "\n")
    print("\n\n\n")
    


