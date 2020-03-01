import datetime

from abc import ABCMeta, abstractmethod
from pprint import pprint

from ..Utils import SQL

################################################################################
################################################################################


yest = datetime.date.today() - datetime.timedelta(1)


################################################################################
################################################################################


class Game(metaclass=ABCMeta):

    def __init__(self, model, gameId):

        self.model = model
        self.gameId = gameId
        self.hasPlayed = False

        self.teams = {"away": None, "home": None}

        self.odds = {}
        self.info = {}
        self.playerStats = {}
        self.teamStats = {"home":{}, "away":{}}

        self.setInfo()


    def __str__(self):
        return self.getName()


    def __repr__(self):
        return "GAME: {}".format(self.gameId)


    def getId(self):
        return self.gameId


    def getPlayerStats(self, playerId, label):
        return self.playerStats[playerId][label]


    def getTeam(self, hA):
        return self.teams[hA]


    def getTeamPlayers(self, hA):
        players = []
        for playerId in self.teamStats[hA]["players"]:
            players.append(self.model.getById("players", playerId))
        return players


    def getInfo(self, item):
        return self.info[item]


    def getTeamStats(self, hA, stat):
        return self.teamStats[hA][stat]


    def getOdds(self, label):
        return self.odds[label]




    def setOdds(self, odds):
        self.odds = odds


    def setTeam(self, hA, team):
        self.teams[hA] = team


################################################################################
################################################################################


class NBAGame(Game):

    def __init__(self, model, gameId):
        super().__init__(model, gameId)


    def setInfo(self):
        self.info["league"] = "nba"
        db = self.model.getDB()
        try:
            self.info["gameTime"], awayId, homeId = db.fetchOne("SELECT game_time, away_id, home_id FROM games WHERE game_id = ?", (self.gameId,))
            odds = dict(zip(("away_spread", "away_ml", "awaySpreadOutcome", "awayMoneyOutcome",
                                "home_spread", "home_ml", "homeSpreadOutcome", "homeMoneyOutcome",
                                "ou", "ouOutcome"), db.fetchOne(SQL.gameOddsCmd, (self.gameId,))))
            self.hasPlayed = True

            for hA, teamId in (("away", awayId), ("home", homeId)):
                self.teamStats[hA] = dict(zip(("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.teamGameStats, (self.gameId, teamId))))

                # for box in range(1,11):
                #     self.teamStats[hA]["shots_{}".format(box)] = dict(zip(("fga", "fgm", "pts"), db.fetchOne(SQL.gameShotStats, (self.gameId, teamId, box))))

                self.teamStats[hA]["players"] = [x[0] for x in db.fetchAll("SELECT player_id FROM player_stats WHERE game_id = ? AND team_id = ? ORDER BY mins DESC", (self.gameId, teamId))]
                for player in db.fetchAll(SQL.playerGameStats.format({"gdCmd": "SELECT game_id FROM games WHERE game_id = {}".format(self.gameId), "scoreWhereCmd": "WHERE ps.team_id = ?"}), (teamId,)):
                    playerId, *playerStats = player
                    self.playerStats[playerId] = dict(zip(("mins", "fga", "fgm", "fta", "ftm",
                                                            "tpa", "tpm", "pts", "reb", "ast",
                                                        "stl", "blk", "trn", "fls", "score"), playerStats))
            self.setOdds(odds)
        except TypeError:
            pass



    def getB2B(self, hA):
        teamId = self.getTeam(hA).getId()
        db = self.model.getDB()
        b2b = db.fetchItem("SELECT b2b FROM team_stats WHERE game_id = ? AND team_id = ?", (self.gameId, teamId))
        if b2b == None:
            b2b = bool(db.fetchItem("SELECT game_id FROM games WHERE year = ? AND game_date = ? AND (home_id = ? OR away_id = ?)", (yest.year, "{}.{}".format(*str(yest).split("-")[1:]), teamId, teamId)))
        return b2b



################################################################################
################################################################################


class NCAABGame(Game):

    def __init__(self, model, gameId):
        super().__init__(model, gameId)


    def setInfo(self):
        self.info["league"] = "ncaab"
        db = self.model.getDB()
        try:
            self.info["gameTime"], awayId, homeId = db.fetchOne("SELECT game_time, away_id, home_id FROM games WHERE game_id = ?", (self.gameId,))

            odds = dict(zip(("away_spread", "away_ml", "awaySpreadOutcome", "awayMoneyOutcome",
                                "home_spread", "home_ml", "homeSpreadOutcome", "homeMoneyOutcome",
                                "ou", "ouOutcome"), db.fetchOne(SQL.gameOddsCmd, (self.gameId,))))
            self.hasPlayed = True

            for hA, teamId in (("away", awayId), ("home", homeId)):
                self.teamStats[hA] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.colGameStats, (self.gameId, teamId))))

                # for box in range(1,11):
                #     self.teamStats[hA]["shots_{}".format(box)] = dict(zip(("fga", "fgm", "pts"), db.fetchOne(SQL.gameShotStats, (self.gameId, teamId, box))))

                self.teamStats[hA]["players"] = [x[0] for x in db.fetchAll("SELECT player_id FROM player_stats WHERE game_id = ? AND team_id = ? ORDER BY mins DESC", (self.gameId, teamId))]
                for player in db.fetchAll(SQL.playerGameStats.format({"gdCmd": "SELECT game_id FROM games WHERE game_id = {}".format(self.gameId), "scoreWhereCmd": "WHERE ps.team_id = ?"}), (teamId,)):
                    playerId, *playerStats = player
                    self.playerStats[playerId] = dict(zip(("mins", "fga", "fgm", "fta", "ftm",
                                                            "tpa", "tpm", "pts", "reb", "ast",
                                                        "stl", "blk", "trn", "fls", "score"), playerStats))
            self.setOdds(odds)
        except TypeError:
            pass
