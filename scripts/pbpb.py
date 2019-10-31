import os
import json
from bs4 import BeautifulSoup
from pprint import pprint
from urllib.request import urlopen, urlretrieve, Request
from urllib.error import HTTPError
from datetime import date, timedelta

gameKeys = ("away_team_id", "gameid", "home_team_id", "lineups", "odds",
            "pitches", "play_by_play", "stadium", "stadium_id", "winning_team_id")


startDate = date.today()
endDate = date(2019,7,7)

mainUrl = "https://sports.yahoo.com"
scoreboardUrl = "/mlb/scoreboard/?confId=&schedState=2&dateRange={}-{}-{}"
filePath = os.environ["HOME"] + "/Desktop/Baseball/{}.json"
errorPath = os.environ["HOME"] + "/Desktop/Baseball/error.log"
writePath = os.environ["HOME"] + "/FEFelson/MLBProjections/Matchups/{}.json"

headers = {"Host": "sports.yahoo.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Connection": "close",
            "Cache-Control": "max-age=0"}


while startDate < endDate:
    gd = "".join(str(startDate).split("-"))
    gameJson = []
    print(startDate)
    req = Request(mainUrl+scoreboardUrl.format(*str(startDate).split("-")), headers=headers)
    html = urlopen(req)
    parser = BeautifulSoup(html,"lxml")

    urls = []
    for line in parser.text.split("\n"):
        #line = str(line)    
        if "root.App.main" in line:
            
            
            line = ";".join(line.split("root.App.main = ")[1].split(";")[:-1])
        
            for team in [value for key, value in json.loads(line)["context"]["dispatcher"]["stores"]["TeamsStore"]["teams"].items() if "mlb" in key]:
                teamId = team["team_id"].split(".")[-1]
                url = team["sportacularLogo"]

##                req = Request(url, headers=headers)
##                html = urlopen(req)
                pprint(html.read())
                urlretrieve(url,"/home/ededub/FEFelson/MLBProjections/Teams/Logos/{}.png".format(teamId)) 

      
                
    startDate += timedelta(1)
            
    
    
