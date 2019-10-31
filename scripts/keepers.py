from bs4 import BeautifulSoup
from pprint import pprint
import unicodedata


teams = ["Felsons", "51s", "lilMoe", "Wootenhaad", "Cadillac", "Generals", "Meatpies", "PC", "Jokers", "Jerzy"] 
cantKeepList = []

roster = {}
price = {}
espn = {}

filePath = "/home/ededub/Documents/"

with open(filePath + "2016.html") as fileIn:
    parser = BeautifulSoup(fileIn, "lxml")
    players2016 = {player.parent.a.string for player in parser.select(".F-icon")}

with open(filePath + "2017.html") as fileIn:
    parser = BeautifulSoup(fileIn, "lxml")
    players2017 = {player.parent.a.string for player in parser.select(".F-icon")}
    for tr in parser.select("td.player"):
        name = tr.a.string
        cost = tr.parent.select(".cost")[0].string[1:]
        price[name] = int(cost) + 5
    
cantKeep = list(players2016 & players2017)

for team in teams:
    roster[team] = []
    with open(filePath + "{}.html".format(team)) as fileIn:
        parser = BeautifulSoup(fileIn, "lxml")
        for td in parser.select("td.first"):
            name = td.parent.a.string
            if name in cantKeep:
                cantKeepList.append((team, name))
            else:
                roster[team].append(name)


with open(filePath + "espn.html") as html:
    parser = BeautifulSoup(html, "lxml")
    for tr in parser.select("aside.inline-table tbody")[0].select("tr"):
        p = tr.select("td")[-2].string[1:]
        if p == "0":
            p = "1"
        espn[tr.a.string] = p 

#pprint(cantKeepList)
#pprint(roster)
#pprint(price)
#pprint(espn)


with open("/home/ededub/Documents/keeperList", "w") as fileOut:
    fileOut.write(format("Can't Keep list", "^50") + "\n\n")
    for team, player in cantKeepList:
        fileOut.write(format(player + " -- " + team, "^50")+"\n")
    fileOut.write("\n\n\n\n")
    fileOut.write(format("Keeper price list", "^50")+"\n\n")
    for team in teams:
        fileOut.write(format(team, "^50")+"\n\n")
        fileOut.write(format("Name", "^30")+format("Price", "^10")+format("ESPN", "^10") + "\n\n")
        for player in roster[team]:
            fileOut.write(format(player, "^30") + format(price.get(player, "--"), "^10"))
            player = unicodedata.normalize("NFD", player)
            player = "".join(c for c in player if not unicodedata.combining(c))
            fileOut.write(format(espn.get(player, "1"), "^10")+"\n\n")
        fileOut.write("\n\n\n")
