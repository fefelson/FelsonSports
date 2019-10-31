from sqlite3 import connect
from matplotlib import pyplot as plt
from pprint import pprint
import datetime
from SportsDB.Models.Player import MLBPlayer
from json import load

filePath = "/home/ededub/FEFelson/MLB.db"

conn = connect(filePath)
curs = conn.cursor()



"""
Single

+3 Pt

Double

+5 Pts

Triple

+8 Pts

Home Run

+10 Pts

Run Batted In

+2 Pts

Run

+2 Pts

Base on Balls

+2 Pts

Hit By Pitch

+2 Pts

Stolen Base

+5 Pts

Pitchers

Inning Pitched

+2.25 Pts

Strikeout

+2 Pts

Win

+4 Pts

Earned Run Allowed

-2 Pts

Hit Against

-0.6 Pts

Base on Balls Against

-0.6 Pts

Hit Batsman

-0.6 Pts

Complete Game

+2.5 Pts

Complete Game Shutout

+2.5 Pts

"""
scorePath = "/home/ededub/FEFelson/MLB/BoxScores/2018/09/07/scoreboard.json"
boxPath = "/home/ededub/FEFelson/MLB/BoxScores/2018/09/07/{}.json"
try:
    with open(scorePath) as fileIn:
        scoreboard = load(fileIn)
    for game in scoreboard["games"]:

        with open(boxPath.format(game["game_id"])) as fileIn:
            boxScore = load(fileIn)
        gameId = game["game_id"]


        gameInfo = {"game_id": gameId,
                    "season": boxScore["season"],
                    "season_type": game["season_type"],
                    "description": game["recap"]["description"],
                    "headline": game["recap"]["description"],
                    "home_id": boxScore["home_team"],
                    "winner_id": boxScore["winning_team"],
                    "game_year": boxScore["game_date"].split("-")[0],
                    "game_day": "{1}.{2}".format(*boxScore["game_date"].split("-")),
                    "venue_id": game["venue"]["venue_id"]}

        gameInfo["loser_id"] = boxScore["team_ids"][0] if boxScore["team_ids"][0] != boxScore["winning_team"] else boxScore["team_ids"][1]
        gameInfo["away_id"] = boxScore["team_ids"][0] if boxScore["team_ids"][0] != boxScore["home_team"] else boxScore["team_ids"][1]

        insert(DB.gamesTable, gameInfo)

        for team in boxScore["teams"]:
            teamId = team["team_id"]
            oppId = boxScore["team_ids"][0] if boxScore["team_ids"][0] != teamId else boxScore["team_ids"][1]

            for player in team["pitchers"]:

                if self.checkEntries(DB.proPlayerTable, "player_id", player["player_id"]):
                    self.databaseManager.sportsManager.downloadPlayer(player["player_id"])
                    self.addPlayer(player["player_id"])

                pitcherStats = player
                pitcherStats["team_id"] = teamId
                pitcherStats["game_id"] = gameId
                pitcherStats["opp_id"] = oppId

                for dec in ("w", "l", "sv", "hld", "blsv"):
                    pitcherStats[dec] = 1 if decConvert[dec] in player["dec"] else 0


                self.insert(pitchingStatsTable, pitcherStats)

                posStats = {"player_id": player["player_id"],
                        "game_id": gameId,
                        "position": player["pos"]}

                self.insert(positionTable, posStats)

            for player in team["batters"]:

                if self.checkEntries(DB.proPlayerTable, "player_id", player["player_id"]):
                    self.databaseManager.sportsManager.downloadPlayer(player["player_id"])
                    self.addPlayer(player["player_id"])

                batterStats = player
                batterStats["team_id"] = teamId
                batterStats["game_id"] = gameId
                batterStats["opp_id"] = oppId


                self.insert(battingStatsTable, batterStats)

                for pos in set(player["pos"]):
                    posStats = {"player_id": player["player_id"],
                        "game_id": gameId,
                        "position": pos}
                    self.insert(positionTable, posStats)

        for pitcher, value in boxScore["pitch_count"].items():
            for i, pitch in enumerate(value):
                pitchType,mph,result = pitch

                pitchData = {
                    "game_id": gameId,
                    "player_id": pitcher,
                    "pitch_number": i,
                    "pitch_type": pitchType,
                    "mph": mph,
                    "result": result
                }
                self.insert(pitchCountTable, pitchData)

        for pitcher, value in boxScore["pitcher_vs_batter"].items():
            for batter, batterValue in value.items():
                batterValue["game_id"] = gameId
                batterValue["pitcher_id"] = pitcher
                batterValue["batter_id"] = batter

                self.insert(pitcherVsBatterTable, batterValue)






except FileNotFoundError:
    pass




conn.close()
