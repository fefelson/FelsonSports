import datetime
import json
import os

from abc import ABCMeta, abstractmethod
from pprint import pprint

from . import Game as GM, Player as PL, Team as TM
from ..DB import NCAAB as NCAABDB, NBA as NBADB
from ..Utils import SQL

################################################################################
################################################################################


gdLabels = ("season", "sixWeeks", "twoWeeks")
gdCmds = (SQL.seasonCmd, SQL.sixWeeksCmd, SQL.twoWeeksCmd)
scorePath = os.environ["HOME"] + "/Yahoo/{}/{}/{}/{}/scoreboard.json"
today = datetime.date.today()


def yId(yahooId):
    return yahooId.split(".")[-1]


################################################################################
################################################################################


class Model(metaclass=ABCMeta):

    gdDict = dict(zip(gdLabels, gdCmds))

    def __init__(self):

        self.db = None
        self.timeFrame = "season"
        self.listeners = {}
        self.items = {"games":{}, "teams": {}, "players": {}}
        self.stats = {}
        self.loadDB()
        self.db.openDB()
        self.setStats()


    def getStats(self, statType, stat):
        try:
            leagueStats = self.stats[self.timeFrame][statType]
        except KeyError:
            self.setStats()
            leagueStats = self.stats[self.timeFrame][statType]
        return leagueStats[stat]


    def setStats(self):
        gdCmd = self.gdDict[self.timeFrame]
        stats = {}
        stats["all_team"] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), self.db.fetchOne(SQL.leagueAvgStats.format({"gdCmd": gdCmd, "andJoinGD": ""}))))
        for hA in ("home", "away"):
            stats["{}_team".format(hA)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), self.db.fetchOne(SQL.leagueAvgStats.format({"gdCmd": gdCmd, "andJoinGD": "AND ts.team_id = gd.{}_id".format(hA)}))))
        for wL in ("winner", "loser"):
            stats["{}_team".format(wL)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), self.db.fetchOne(SQL.leagueAvgStats.format({"gdCmd": gdCmd, "andJoinGD": "AND ts.team_id = gd.{}_id".format(wL)}))))
        self.stats[self.timeFrame] = stats


    def __del__(self):
        self.db.closeDB()


    def addListener(self, key, control):
        self.listeners[key].append(control)


    def onChange(self, key):
        for listener in self.listeners[key]:
            listener.update()


    def setTimeFrame(self, tf):
        self.timeFrame = tf


    def getGames(self, gameDate):
        if gameDate >= today:
            return self.gamePreview(gameDate)
        else:
            return self.gameReview(gameDate)



    def getById(self, itemType, itemId):
        item = self.items[itemType].get(int(itemId), None)
        if not item:
            item = self.getItem(itemType, itemId)
            self.items[itemType][int(itemId)] = item
        return item


    def getDB(self):
        return self.db


    def getTimeFrame(self):
        return self.timeFrame


    @abstractmethod
    def loadDB(self):
        pass


################################################################################
################################################################################


class NCAABModel(Model):

    _positionsList = ("G", "F", "C")

    def __init__(self):
        super().__init__()


    def getItem(self, itemType, itemId):
        newType = {"games": GM.NCAABGame, "teams": TM.NCAABTeam, "players": PL.NCAABPlayer}[itemType]
        return newType(self, itemId)


    def loadDB(self):
        self.db = NCAABDB.NCAABDB()


    def getTeams(self):
        teams = []
        for teamId in [x[0] for x in self.db.fetchAll("SELECT team_id FROM col_teams")]:
            teams.append(self.getById("teams", teamId))
        return teams


    def gamePreview(self, gameDate):
        games = []
        with open(scorePath.format("ncaab", *str(gameDate).split("-"))) as fileIn:
            matchInfo = json.load(fileIn)

            for game in [g for g in matchInfo["games"].values() if gameDate == (datetime.datetime.strptime(g["game_time"],"%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=4)).date()]:
                try:
                    awayId = yId(game["away_id"])
                    homeId = yId(game["home_id"])
                    gameId = yId(game["game_id"])
                    try:
                        odds = [x for x in game["odds"].values()][0]
                        try:
                            odds["ou"] = float(odds["total"])
                        except ValueError:
                            odds["ou"] = 0
                    except IndexError:
                        odds = {}

                    newGame = self.getById("games", gameId)

                    #### dirty hack
                    newGame.info["gameTime"] = game["game_time"]
                    #####

                    homeTeam = self.getById("teams", homeId)
                    awayTeam = self.getById("teams", awayId)
                    newGame.setTeam("home", homeTeam)
                    newGame.setTeam("away", awayTeam)
                    newGame.setOdds(odds)
                    games.append(newGame)
                except TypeError:
                    pass
        games = sorted(games, key=lambda x: datetime.datetime.strptime(x.getInfo("gameTime"), "%a, %d %b %Y %H:%M:%S %z"))
        return games


    def gameReview(self, gameDate):
        games = []
        for gameId, awayId, homeId in self.db.fetchAll("SELECT game_id, away_id, home_id FROM games WHERE year = ? AND game_date = ?", (gameDate.year, "{}.{}".format(*str(gameDate).split("-")[1:]) )):
            try:
                newGame = self.getById("games", gameId)
                homeTeam = self.getById("teams", homeId)
                awayTeam = self.getById("teams", awayId)
                newGame.setTeam("home", homeTeam)
                newGame.setTeam("away", awayTeam)
                games.append(newGame)
            except TypeError:
                pass
        return games

################################################################################
################################################################################


class NBAModel(Model):

    _positionsList = ("G", "F", "C")

    def __init__(self):
        super().__init__()


    def getItem(self, itemType, itemId):
        newType = {"games": GM.NBAGame, "teams": TM.NBATeam, "players": PL.NBAPlayer}[itemType]
        return newType(self, itemId)


    def loadDB(self):
        self.db = NBADB.NBADB()


    def getTeams(self):
        teams = []
        for teamId in [x[0] for x in self.db.fetchAll("SELECT team_id FROM pro_teams")]:
            teams.append(self.getById("teams", teamId))
        return teams


    def gamePreview(self, gameDate):
        games = []
        with open(scorePath.format("nba", *str(gameDate).split("-"))) as fileIn:
            matchInfo = json.load(fileIn)

            for game in [g for g in matchInfo["games"] if gameDate == (datetime.datetime.strptime(g["game_time"],"%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=4)).date()]:
                awayId = yId(game["away_id"])
                homeId = yId(game["home_id"])
                gameId = yId(game["game_id"])
                try:
                    odds = [x for x in game["odds"].values()][0]
                    try:
                        odds["ou"] = float(odds["total"])
                    except ValueError:
                        odds["ou"] = 0
                except IndexError:
                    odds = {}

                newGame = self.getById("games", gameId)

                #### dirty hack
                newGame.info["gameTime"] = game["game_time"]
                #####

                homeTeam = self.getById("teams", homeId)
                awayTeam = self.getById("teams", awayId)
                newGame.setTeam("home", homeTeam)
                newGame.setTeam("away", awayTeam)
                newGame.setOdds(odds)
                games.append(newGame)
        games = sorted(games, key=lambda x: datetime.datetime.strptime(x.getInfo("gameTime"), "%a, %d %b %Y %H:%M:%S %z"))
        return games


    def gameReview(self, gameDate):
        games = []
        for gameId, awayId, homeId in self.db.fetchAll("SELECT game_id, away_id, home_id FROM games WHERE year = ? AND game_date = ?", (gameDate.year, "{}.{}".format(*str(gameDate).split("-")[1:]) )):
            newGame = self.getById("games", gameId)
            homeTeam = self.getById("teams", homeId)
            awayTeam = self.getById("teams", awayId)
            newGame.setTeam("home", homeTeam)
            newGame.setTeam("away", awayTeam)
            games.append(newGame)
        return games
