import datetime
import json
import os.path

import MLBProjections.MLBProjections.DB.MLB as DB

from pprint import pprint

teamCmd = "SELECT abrv, color FROM pro_teams WHERE team_id = ?"
awayLineupCmd = "SELECT lineups.player_id, first_name, last_name FROM lineups INNER JOIN pro_players ON lineups.player_id = pro_players.player_id INNER JOIN game_meta ON lineups.team_id = game_meta.away_id ORDER BY batt_order"
homeLineupCmd = "SELECT lineups.player_id, first_name, last_name FROM lineups INNER JOIN pro_players ON lineups.player_id = pro_players.player_id INNER JOIN game_meta ON lineups.team_id = game_meta.home_id ORDER BY batt_order"


mlbDB = DB.MLBDatabase()
mlbDB.openDB()

today = datetime.date.today()


filePath = "/home/ededub/FEFelson/MLBProjections/Lineups/{}.json".format("".join(str(today).split("-")))
dbPath = "/home/ededub/FEFelson/MLBProjections/Games/{}.db"


games = []

with open(filePath) as fileIn:
    info = json.load(fileIn)["matchups"]


for game in info:
    homeId = game["homeTeam"]["teamId"]
    awayId = game["awayTeam"]["teamId"]
    homeAbrv, homeColor = mlbDB.fetchOne(teamCmd, (homeId,))
    awayAbrv, awayColor = mlbDB.fetchOne(teamCmd, (awayId,))

    data = {"gameId": game["gameId"],
            "homeId": homeId,
            "homeAbrv": homeAbrv,
            "homeColor": homeColor,
            "awayId": awayId,
            "awayAbrv": awayAbrv,
            "awayColor": awayColor
            }

    games.append(data)

for i, game in enumerate(games):
    print(i, game["gameId"].split("390623")[-1])
    print("{} vs {}\n".format(game["awayAbrv"],game["homeAbrv"]))


gameId = "390623{}".format(str(input()))

if os.path.exists(dbPath.format(gameId)):
    gameDB = DB.MLBGame(gameId)
    gameDB.openDB()
    print("AWAY team")
    pprint(gameDB.fetchAll(awayLineupCmd))
    print("\nHome team")
    pprint(gameDB.fetchAll(homeLineupCmd))
    gameDB.closeDB()
else:
    print("no")

mlbDB.closeDB()




            
    


    
