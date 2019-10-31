import json
import os

from bs4 import BeautifulSoup
from pprint import pprint
from urllib.request import urlopen, Request


def dld(url, headers):
    req = Request(url, headers=headers)
    html = urlopen(req)
    parser = BeautifulSoup(html,"lxml")
    return parser
    


def yahooDld(url):
    item = None
    headers["Host"] = "sports.yahoo.com"
    parser = dld(url, headers)
    

    for line in parser.text.split("\n"):
        if "root.App.main" in line:
            item = json.loads(";".join(line.split("root.App.main = ")[1].split(";")[:-1]))["context"]["dispatcher"]["stores"]

    return item

def espnDld(url):
    item = None
    headers["Host"] = "www.espn.com"
    parser = dld(url)
    


league = "mlb"

baseYahoo = "https://sports.yahoo.com"
teamPath = os.environ["HOME"]+"/FEFelson/NFLProjections/Teams/"
destPath = os.environ["HOME"]+"/FelsonSports/FelsonSports/DB/Teams/{0[league]}.json".format({"league":league})

teams = []



headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Connection": "close",
            "Cache-Control": "max-age=0"}

url = "https://sports.yahoo.com/{}/teams/".format(league)

info = yahooDld(url)
for team in [value for key, value in info["TeamsStore"]["teams"].items() if league in key]:
##    pprint(team)
##    print("\n\n\n")
    data = yahooDld(baseYahoo + team["navigation_links"]["team_home"]["url"])["TeamsStore"]
    x = data["teams"][team["team_id"]]
    newInfo = {}
    newInfo["abrv"] = x["abbr"]
    newInfo["team_id"] = league+str(team["team_id"].split(".")[-1])
    newInfo["conference"] = x["conference"]
    newInfo["division"] = x["division"]
    newInfo["primary_color"] = x["colorPrimary"]
    newInfo["secondary_color"] = x["colorSecondary"]
    newInfo["first_name"] = x["first_name"]
    newInfo["last_name"] = x["last_name"]
    newInfo["league"] = league
    newInfo["yahoo_id"] = team["team_id"]
    newInfo["espn_id"] = str(team["team_id"].split(".")[-1])
    pprint(newInfo)
    teams.append(newInfo)
    print("\n\n\n")


with open(destPath, 'w') as fileOut:
    json.dump({"teams":teams}, fileOut)




