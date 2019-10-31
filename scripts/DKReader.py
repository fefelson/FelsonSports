import csv
import os
import sqlite3
from pprint import pprint
import datetime
import json
import MLBProjections.MLBProjections.DB.MLB as DB
import re
##import unicodedata
##
##
##def normal(name):
##    name = unicodedata.normalize("NFD", name)
##    name = "".join(c for c in name if not unicodedata.combining(c))
##    return name


def splitName(name):
    firstName = None
    lastName = None
    name = name.split()
    if len(name) == 2:
        firstName, lastName = name
    elif len(name) == 3 and (name[-1][-1] == "." or name[-1] in ("Jr", "Sr", "II", "III", "IV", "V")):
        firstName = name[0]
        lastName = " ".join(name[1:])
    elif len(name) == 3 and len(name[1]) == 2 and name[1][-1] == ".":
        firstName = " ".join(name[:2])
        lastName = name[2]
    else:
        index = int(input(name))
        firstName = " ".join(name[:index])
        lastName = " ".join(name[index:])
    return firstName, lastName


def setGameDate(games):
    return games[0].split()[1]


def setStartTime(games):
    startTimes = []
    for game in games:
        try:
            gameTime = re.sub("AM|PM", "", game.split()[-2])
            startTimes.append(float(re.sub(":",".",gameTime)))
        except IndexError:
            pass
    return min(startTimes)


def setGameId(game, fantasyDB, mlbDB):
    gameId = None
    games = []
    try:
        homeAbrv = game.split()[0].split("@")[-1]
        awayAbrv = game.split()[0].split("@")[0]
        homeId = getTeamId(homeAbrv, fantasyDB, mlbDB)
        awayId = getTeamId(awayAbrv, fantasyDB, mlbDB)

        itemDate = game.split()[1].split("/")

        gameTime = datetime.datetime.strptime(game.split()[-2], "%I:%M%p")
        if game.split()[-1] == "ET":
            gameTime += datetime.timedelta(hours=4)
        
        with open(scoreboardPath.format(itemDate[-1], itemDate[0], itemDate[1])) as fileIn:
            games = json.load(fileIn)

        for info in games["games"]:
            if int(info["game_time"][0].split(":")[0]) == int(gameTime.hour) and int(homeId) == int(info["home_id"]) and int(awayId) == int(info["away_id"]):
                gameId = info["game_id"]
                break
    except IndexError:
        pass
    return gameId


def getTeamId(team, fantasyDB, mlbDB):
    try:
        teamId = fantasyDB.fetchOne("SELECT team_id FROM dk_team WHERE dk_id = ?",(team,))[0]
    except TypeError:
        teamId = getDBTeamId(team, fantasyDB, mlbDB)
    return teamId
    


def getGameIds(games, fantasyDB, mlbDB):
    gameIds = {}
    for game in games:
        newGame = setGameId(game, fantasyDB, mlbDB)
        if newGame:
            gameIds[game] = newGame
    print(gameIds)
    return gameIds
    


def getDBTeamId(team, fantasyDB, mlbDB):
    teams = mlbDB.fetchAll("SELECT team_id FROM pro_teams WHERE abrv = ?",(team,))
    if len(teams) == 1:
        teamId = teams[0][0]
    else:
        pprint(mlbDB.fetchAll("SELECT team_id, abrv FROM pro_teams"))
        teamId = input(team)
    fantasyDB.insert(DB.dkTeamTable, values=[team, teamId])
    return teamId


def getPlayerId(fullName, team, fantasyDB, mlbDB):
    playerId = None
    firstName, lastName = splitName(fullName)
    players = mlbDB.fetchAll("SELECT player_id FROM pro_players WHERE first_name = ? AND last_name = ?",(firstName, lastName))
    if len(players) == 1:
        playerId = players[0][0]
        fantasyDB.insert(DB.dkYahooTable, values=[fullName, playerId, team])
    else:
        pprint(mlbDB.fetchAll("SELECT player_id, first_name, last_name FROM pro_players WHERE first_name = ?",(firstName,)))
        pprint(mlbDB.fetchAll("SELECT player_id, first_name, last_name FROM pro_players WHERE last_name = ?",(lastName,)))

        try:
            playerId = int(input(team+"   "+name))
            fantasyDB.insert(DB.dkYahooTable, values=[fullName, playerId, team])
        except (TypeError, ValueError):
            pass
    return playerId
        
    

mlbDB = DB.MLBDatabase()
mlbDB.openDB()


fantasyDB = DB.MLBDFS()
fantasyDB.openDB()


##fantasyDB.executeCmd("DROP TABLE dk_sheets")
##fantasyDB.executeCmd(DB.dkSheetTable.createTableCmd())
##fantasyDB.executeCmd("DROP TABLE dk_prices")
##fantasyDB.executeCmd(DB.dkPriceTable.createTableCmd())
##fantasyDB.executeCmd("DROP TABLE dk_sheet_games")
##fantasyDB.executeCmd(DB.dkSheetGamesTable.createTableCmd())

##fantasyDB.executeCmd("DELETE FROM dk_prices WHERE dk_sheet_id IN (12,13) ")
##fantasyDB.executeCmd("DELETE FROM dk_sheets WHERE dk_sheet_id IN (12,13)")
##fantasyDB.executeCmd("DELETE FROM dk_sheet_games WHERE dk_sheet_id IN (12,13)")

today = datetime.date.today()

dkPath = os.environ["HOME"] + "/Downloads/"
scoreboardPath = os.environ["HOME"] + "/FEFelson/MLBProjections/PlayByPlay/{}/{}/{}/scoreboard.json"




players = []
gameDate = None
gameType = "classic"



for fileName in os.listdir(dkPath):
    sheetId = None
    games = []
    if "DKSalaries" in fileName:
        with open(dkPath+fileName) as f:
            f_csv = csv.reader(f)
            # Skip past column headers
            f_csv.__next__()
            _,_,name,_,pos,price,game,team,avgScore = f_csv.__next__()
            if pos != "P":
                continue

        with open(dkPath+fileName) as f:
            f_csv = csv.reader(f)
            # Skip past column headers
            f_csv.__next__()
 
            for row in (f_csv):
        ##        print(row)
                playerId = -1
                # Position, Name+ID, Name, ID, Roster Position,	Salary,	Game Info, TeamAbbrev, AvgPointsPerGame
                _,_,name,_,pos,price,game,team,avgScore = row
                if name != "":    
                    games.append(game)

        games = list(set(games))
        gameIds = getGameIds(games, fantasyDB, mlbDB)
        numGames = len(gameIds.values())
        gameDate = setGameDate(games)
        startTime = setStartTime(games)

        try:
            fantasyDB.fetchOne("SELECT dk_sheet_id FROM dk_sheets WHERE game_type = ? AND start_time = ? AND num_games = ? AND game_date = ?",(gameType, startTime, numGames, gameDate))[0]
        except TypeError:
            sheetId = fantasyDB.nextKey(DB.dkSheetTable)

        if sheetId:
            fantasyDB.insert(DB.dkSheetTable, values=[sheetId, gameType, startTime, numGames, gameDate])
            for gameId in gameIds.values():
                sheetGameId = fantasyDB.nextKey(DB.dkSheetGamesTable)
                fantasyDB.insert(DB.dkSheetGamesTable, values=[sheetGameId, sheetId, gameId])


            with open(dkPath+fileName) as f:
                f_csv = csv.reader(f)
                # Skip past column headers
                f_csv.__next__()
                for row in (f_csv):
            ##        print(row)
                    # Position, Name+ID, Name, ID, Roster Position,	Salary,	Game Info, TeamAbbrev, AvgPointsPerGame
                    _,_,name,_,pos,price,game,team,avgScore = row
                    a,h = game.split()[0].split("@")
                    opp = a if a != team else h
                    gameId = gameIds[game]
                    playerId = -1
                    if name != "":
                        try:
                            playerId = fantasyDB.fetchOne("SELECT yahoo_id FROM dk_yahoo WHERE dk_id = ? AND team_id = ?",(name,team))[0] 
                        except TypeError:
                            playerId = getPlayerId(name, team, fantasyDB, mlbDB)
                        
                        pos = ",".join(pos.split("/"))

                        try:
                            dkPriceId = fantasyDB.fetchItem("SELECT dk_price_id FROM dk_prices WHERE dk_id = ? AND game_id = ?", (name, gameId))
                        except TypeError:
                            dkPriceId = fantasyDB.nextKey(DB.dkPriceTable)
                            fantasyDB.insert(DB.dkPriceTable, values=[dkPriceId, team, opp, gameId, name, price, pos])

                        sheetPlayersId = fantasyDB.nextKey(DB.dkSheetPlayersTable)
                        fantasyDB.insert(DB.dkSheetPlayersTable, values=[sheetPlayersId, sheetId, dkPriceId])
                        print(playerId, pos, avgScore)

        os.remove(dkPath+fileName)

            
        

   

fantasyDB.commit()
mlbDB.closeDB()

fantasyDB.closeDB()

                

