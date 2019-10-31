import json
from pprint import pprint
import os
import NFLProjections.NFLProjections.DB.NFL as DB
import re

filePath = "/home/ededub/FEFelson/NFLProjections/BoxScore/{}/{}/"
teamPath = "/home/ededub/FEFelson/NFLProjections/Teams/"


def safeValue(value):
    if value == "N/A":
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    elif ":" in value:
        return ".".join(value.split(":")[1:])
    elif "-" in value:
        return re.sub("-",".",value)
    else:
        return value


def rId(yahooId):
    if isinstance(yahooId, int) or yahooId == None:
        return yahooId
    return yahooId.split(".")[-1]

nflDB = DB.NFLDatabase()
nflDB.openDB()

playerStatTypes = [x[0] for x in nflDB.fetchAll("SELECT stat_id FROM stat_types WHERE stat_id < 900")]
teamStatTypes = [x[0] for x in nflDB.fetchAll("SELECT stat_id FROM stat_types")]

for season in range(2019,2020):
    for week in [week for week in range(2,3) if week != 21]:
        gamePath = filePath.format(season,week)
        for fileName in [fileName for fileName in os.listdir(gamePath) if "scoreboard" not in fileName]:
            with open(gamePath+fileName) as fileIn:
                info = json.load(fileIn)
                awayPts =0
                homePts =0
                for period in info["game_periods"]:
                    awayPts += int(period["away_points"])
                    homePts += int(period["home_points"])

                gameId = rId(info["game_id"])
                homeId = rId(info["home_id"])
                awayId = rId(info["away_id"])
                winnerId = rId(info["winner_id"])
                loserId = None
                if winnerId != None:
                    loserId = homeId if winnerId == awayId else awayId
                stadiumId = rId(info["stadium_id"])
                gameType = info["game_type"]
                gameTime = info["game_time"]
                outcome = rId(info["outcome"])

                nflDB.insert(DB.gamesTable, values=[gameId, homeId, awayId, winnerId, loserId, stadiumId, season, week, gameType, gameTime, outcome])
                teamStatId = nflDB.nextKey(DB.teamStatsTable)
                nflDB.insert(DB.teamStatsTable, values=[teamStatId, gameId, homeId, awayId, 1000, homePts])
                teamStatId = nflDB.nextKey(DB.teamStatsTable)
                nflDB.insert(DB.teamStatsTable, values=[teamStatId, gameId, awayId, homeId, 1000, awayPts])

            
                for player in info["players"]:
                    playerId = player["player_id"]
                    teamId = player["team_id"]
                    oppId = homeId if teamId == awayId else awayId
                    #pprint(player)
                    stats = info["playerStats"].pop("nfl.p.{}".format(player["player_id"]), {})
                    for statId in playerStatTypes:
                        value = safeValue(stats.get("nfl.stat_type.{}".format(statId), 0))
                        playerStatId = nflDB.nextKey(DB.playerStatsTable)
                        if int(statId) in playerStatTypes:
                            nflDB.insert(DB.playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, statId, value]) 
                      
                for key, value in info.get("homeTeamStats", {}).items():
                    teamStatId = nflDB.nextKey(DB.teamStatsTable)
                    oppId = awayId
                    teamId = homeId
                    value = safeValue(value)
                    statId = rId(key)
                    if int(statId) in teamStatTypes:
                        nflDB.insert(DB.teamStatsTable, values=[teamStatId, gameId, teamId, oppId, statId, value])
                    
                for key, value in info.get("awayTeamStats", {}).items():
                    teamStatId = nflDB.nextKey(DB.teamStatsTable)
                    oppId = awayId
                    teamId = homeId
                    value = safeValue(value)
                    statId = rId(key)
                    if int(statId) in teamStatTypes:
                        nflDB.insert(DB.teamStatsTable, values=[teamStatId, gameId, teamId, oppId, statId, value])


nflDB.commit()
nflDB.closeDB()




##with open(filePath) as fileIn:
##   pprint(json.load(fileIn))
##   raise AssertionError


   




