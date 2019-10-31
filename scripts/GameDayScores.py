from json import dump, load
from csv import reader
from sqlite3 import connect, ProgrammingError
from os import environ, walk
from pprint import pprint
from itertools import chain
from datetime import date, timedelta
from SportsDB.WebService.ESPN import TeamParser as TP
import operator
import numpy

league = "NBA"
season = 2019
filePath = environ["HOME"] + "/FEFelson/{}/BoxScores"

for dirPath, dirNames, fileNames in walk(filePath.format(league)):
    if 'scoreboard.json' in fileNames:
        gameIds = []
        players = []
        with open(dirPath+"/scoreboard.json") as fileIn:
            gameIds = [game["game_id"] for game in load(fileIn)["games"]]
        for gameId in gameIds:
            try:
                with open(dirPath +"/{}.json".format(gameId)) as gameIn:
                    game = load(gameIn)
                    for team in game["teams"]:
                        for player in team["players"]:
                            score = 0
                            try:
                                score += int(player["points"])
                                score += int(player["tpm"])* .5
                                score += (int(player["oreb"])+int(player["dreb"])) * 1.25
                                score += int(player["ast"]) * 1.5
                                score += int(player["stl"]) * 2
                                score += int(player["blk"]) * 2
                                score += int(player["turn"]) * -.5

                                total = 0
                                for stat in (int(player["points"]), (int(player["oreb"]) + int(player["dreb"])), int(player["ast"]), int(player["stl"]), int(player["blk"])):
                                    if stat >= 10:
                                        total += 1
                                if total >= 2:
                                    score += 1.5

                                if total >=3:
                                    score += 3
                            except ValueError:
                                pass

                            players.append({"player_id":player["player_id"],"name": player["name"], "score":score})
            except FileNotFoundError:
                pass
        players = sorted(players, key= lambda x: x["score"], reverse=True)
        pprint(players)

        if players:
            with open(dirPath +"/results.json", "w") as fileOut:
                dump(players, fileOut)

                                 
                        
                      




