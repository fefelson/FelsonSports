from bs4 import BeautifulSoup
from json import load
from pprint import pprint
import re
from unicodedata import normalize, combining
from os import walk
from collections import Counter



def normal(name):
    name = normalize("NFD", name)
    name = "".join(c for c in name if not combining(c))
    return name


def getName(line, pitcher=False):
    newName = []
    result = []

    line = normal(line)
    
    for i, name in enumerate(line.split()):
        if name[0] == name[0].capitalize() or i == 0:
            newName.append(name)
        else:
            break

    result = line.split(" ".join(newName))[1:]
    return (" ".join(newName), " ".join(result).split(",")[0].strip())


def getId(playerName, playerDict):
    playerId = -1
    for key, value in playerDict.items():
        if playerName == key:
            playerId = value
            break
        elif playerName in key:
            playerId = value
            break
    return playerId
    
    


parser = {}




teams = {}


with open("/home/ededub/Documents/playByPlay.html") as fileIn:
    parser["pbp"] = BeautifulSoup(fileIn, "lxml")

with open("/home/ededub/Documents/boxScore.html") as fileIn:
    parser["bs"] = BeautifulSoup(fileIn, "lxml")



teamHtml = parser["bs"].select(".boxscore-2017__wrap")
for i in range(2):
    teamName = teamHtml[i].header.img["alt"]
    team = teams.get(teamName, {})

    batters = {}
    pitchers = {}

    batTable = teamHtml[i].select("article")[0].select("table")[0]
    pitchTable = teamHtml[i-1].select("article")[1].select("table")[0]
    for batter in batTable.select("tbody.athletes"):
        batterName = batter.select(".name a span")[0].string
        batters[batterName] = batter["data-athlete-id"]
    for pitcher in pitchTable.select("tbody.athletes"):
        pitcherName = pitcher.select(".name a span")[0].string
        pitchers[pitcherName] = pitcher["data-athlete-id"]

    team["batterId"] = batters
    team["pitcherId"] = pitchers

    teams[teamName] = team

pprint(teams)
    
    



for section in parser["pbp"].select("#allPlays section"):
    teamAbrv = section.select("header img")[0]["alt"]
    team = teams.get(teamAbrv, {})
    pitchers = team.get("pitchers", {})
    for li in section.select("li"):

        if "info-row--pitcher" in li.attrs["class"] and li.select(".left .headline")[0].text:
            name = li.select(".left .headline")[0].text
            if name:
                pitcherName, _ = getName(name, True)
                pitcherId = getId(pitcherName, team["pitcherId"])
        elif "info-row--change" not in li.attrs["class"] and "info-row--footer" not in li.attrs["class"] and li.select(".left .headline")[0].string:
            name = li.select(".left .headline")[0].string
            pitcherLog = pitchers.get(pitcherId, {})
            batterName, result = getName(name)
            batterId = getId(batterName, team["batterId"])

            atbats = pitcherLog.get("atbats", {})
            batterLog = atbats.get(batterId, {"ab":0, "hbp": 0, "bb":0, "h":0, "dbl":0, "tpl":0, "hr":0})
            if "walked" in result:
                batterLog["bb"] = batterLog["bb"] + 1
            elif "hit by" in result:
                batterLog["hbp"] = batterLog["hbp"] + 1
            else:
                batterLog["ab"] = batterLog["ab"] + 1
                if "singled" in result:
                    batterLog["h"] = batterLog["h"] + 1
                elif "doubled" in result:
                    batterLog["h"] = batterLog["h"] + 1
                    batterLog["dbl"] = batterLog["dbl"] + 1
                elif "tripled" in result:
                    batterLog["h"] = batterLog["h"] + 1
                    batterLog["tpl"] = batterLog["tpl"] + 1
                elif "homered" in result:
                    batterLog["h"] = batterLog["h"] + 1
                    batterLog["hr"] = batterLog["hr"] + 1
                
            atbats[batterId] = batterLog
            pitcherLog["atbats"] = atbats

            pitches = li.select("tbody tr")
            for i,pitch in enumerate(pitches):
                pitchCount = pitcherLog.get("pitches", [])
                result = pitch.td.span.next_sibling.string
                if "Strike" in result:
                    result = "Strike"
                elif "Out" in result:
                    result = "Out"
                elif "Foul" in result:
                    result = "Foul"
                elif "Single" in result or "Double" in result or "Triple" in result:
                    result = "Hit"
                if result == "Strike" and i+1 == len(pitches):
                    result = "Strike Out"
                
                pitchType = pitch.select(".type")[0].string
                if "FB" in pitchType:
                    pitchType = "Fastball"
                elif " Curve" in pitchType:
                    pitchType = "Curve"
                mph = pitch.select(".mph")[0].string
                pitchCount.append((pitchType, mph, result))
                pitcherLog["pitches"] = pitchCount

            pitchers[pitcherId] = pitcherLog
    team["pitchers"] = pitchers    
    teams[teamAbrv] = team


    

for team,info in teams.items():
    print(team+"\n\n")
    pprint(info)
    print("\n\n\n")

    
    
