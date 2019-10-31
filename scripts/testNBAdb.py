import sqlite3
from os import walk
from json import load
import datetime
from pprint import pprint



teamStatList = ["fgm", "fga", "ftm", "fta", "tpm", "tpa", "reb", "oreb", "dreb", "ast", "stl", "blk", "trn", "ptsOffTrn", "fstBrkPts", "ptsInPnt", "fls", "pts"]
playerStatList = ["min", "fgm", "fga", "ftm", "fta", "tpm", "tpa", "reb", "oreb", "dreb", "ast", "stl", "blk", "trn", "plsMin", "fls", "pts"]






gamesTable = "CREATE TABLE games ( gameId TEXT, homeId TEXT, awayId TEXT, venueId TEXT, winnerId TEXT, loserId TEXT, season INTEGER, gameYear INTEGER, gameDay REAL)"#, headline TEXT, description TEXT)"
teamsTable = "CREATE TABLE teams ( teamId TEXT, name TEXT, abrv TEXT, color TEXT, altColor TEXT)"
playersTable = "CREATE TABLE players ( playerId TEXT, name TEXT)"#, lastName TEXT, birthYear INTEGER, birthDay REAL, height REAL, weight INTEGER, debutYr INTEGER)"
teamStatsTable = "CREATE TABLE teamStats ( gameId TEXT, teamId TEXT, oppId TEXT, fgm INTEGER, fga INTEGER, ftm INTEGER, fta INTEGER, tpm INTEGER, tpa INTEGER, reb INTEGER, oreb INTEGER, dreb INTEGER, ast INTEGER, stl INTEGER, blk INTEGER, trn INTEGER, ptsOffTrn INTEGER, fstBrkPts INTEGER, ptsInPnt INTEGER, fls INTEGER, pts INTEGER)"
playerStatsTable = "CREATE TABLE playerStats (gameId TEXT, playerId TEXT, teamId TEXT, oppId TEXT, min INTEGER, fgm INTEGER, fga INTEGER, ftm INTEGER, fta INTEGER, tpm INTEGER, tpa INTEGER, reb INTEGER, oreb INTEGER, dreb INTEGER, ast INTEGER, stl INTEGER, blk INTEGER, trn INTEGER, plsMin INTEGER, fls INTEGER, pts INTEGER)"
draftkingsTable = "CREATE TABLE draftkings (gameId TEXT, playerId TEXT, oppId TEXT, price INTEGER)"

conn = sqlite3.connect("/home/ededub/FEFelson/NBA/NBA.db")
curs = conn.cursor()

for cmd in (gamesTable, teamsTable, playersTable, teamStatsTable, playerStatsTable, draftkingsTable):
    print(cmd)
    curs.execute(cmd)

with open("/home/ededub/FEFelson/NBA/teams.dat") as fileIn:
    cmd = "INSERT INTO teams VALUES (?,?,?,?,?)"
    for i, line in enumerate(fileIn):
        if i > 0:
            line = line.split("|")
            curs.execute(cmd, (line[2].strip(), line[0].strip(), line[1].strip(), line[3].strip(), line[4].strip()))


with open("/home/ededub/FEFelson/NBA/playrs.dat") as fileIn:
    cmd = "INSERT INTO players VALUES (?,?)"
    for i, line in enumerate(fileIn):
        if i > 0:
            line = line.split("|")
            curs.execute(cmd, (line[0].strip(), line[1].strip()))





for filePath, _, fileNames in walk("/home/ededub/FEFelson/NBA/BoxScores"):
    for name in fileNames:
        if name != "scoreboard.json" and name[0] != "M":
            print(filePath+"/"+name) 
            with open(filePath+"/"+name) as fileIn:
                bs = dict(load(fileIn))
                gameId = bs["gameId"]
                teams = bs["teamIds"]
                winner = bs["winningTeam"]
                home = bs["homeTeam"]
                away = teams[0] if teams[0] != home else teams[1]
                loser = teams[0] if teams[0] != winner else teams[1]

                season = bs["season"]
                gameYear = bs["gameDate"].split("-")[0]
                gameDay = ".".join(bs["gameDate"].split("-")[1:])

                gameStats = [gameId, home, away, "N/A", winner, loser, season, gameYear, gameDay]#, headline, description]
                cmd = "INSERT INTO games VALUES(?,?,?,?,?,?,?,?,?)"
                curs.execute(cmd, gameStats)
                
                for team in bs["teams"]:
                    teamId = team["teamId"]
                    oppId = teams[0] if teams[0] != teamId else teams[1]

                    teamStats = [gameId, teamId, oppId] + [team["stats"][key] for key in teamStatList]
                    cmd = "INSERT INTO teamStats VALUES(" + ",".join("?" for x in teamStats)+")"
                    curs.execute(cmd, teamStats)
                    
                    for player in team["players"]:
                        playerId = player["playerId"]

                        playerStats = [gameId, playerId, teamId, oppId] + [player["stats"][key] for key in playerStatList]
                        cmd = "INSERT INTO playerStats VALUES(" + ",".join("?" for x in playerStats)+")"
                    curs.execute(cmd, playerStats)



            
conn.commit()
conn.close()
