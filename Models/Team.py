import datetime
import os

from ..Utils import SQL

# from pprint import pprint

################################################################################
################################################################################


logoPath = os.environ["HOME"] + "/Yahoo/{}/teams/{}.png"


################################################################################
################################################################################


class Team:

    def __init__(self, model, teamId):

        self.model = model
        self.teamId = teamId

        self.info = {}
        self.stats = {}

        self.listeners = {}
        self.setInfo()

    def __str__(self):
        return "{} {}".format(self.info["firstName"], self.info["lastName"])


    def __repr__(self):
        return "Team: {}".format(self.info["abrv"])


    def addListener(self, lType, control):
        self.listeners[lType] = self.listeners.get(lType, []).append(control)


    def getName(self):
        return str(self)


    def getPlayers(self):
        db = self.model.getDB()
        players = []
        for playerId in [x[0] for x in db.fetchAll("SELECT player_id FROM player_stats WHERE team_id = ? AND game_id = (SELECT MAX(game_id) FROM games WHERE home_id =? OR away_id = ?)", (self.teamId, self.teamId, self.teamId))]:
            players.append(self.model.getById("players", playerId))

        return players


    def getOdds(self, n):
        db = self.model.getDB()


    def getSpreadGames(self):
        db = self.model.getDB()
        return db.fetchAll(SQL.spreadResultCmd, (self.teamId,))



    def getId(self):
        return self.teamId


    def getInfo(self, item):
        return self.info[item]


    def onChange(self, lType):
        for listen in self.listeners[lType]:
            listen.update()


    def getStats(self, statType, stat):
        timeFrame = self.model.getTimeFrame()
        try:
            teamStats = self.stats[timeFrame][statType]
        except KeyError:
            self.setStats()
            teamStats = self.stats[timeFrame][statType]
        return teamStats[stat]


    def getGames(self, n=None):
        games = []
        db = self.model.getDB()
        cmd = "SELECT game_id, away_id, home_id FROM games WHERE season = 2019 AND (home_id = ? OR away_id = ?) ORDER BY game_id DESC"
        if n:
            cmd += " LIMIT {}".format(n)
        for gameId, awayId, homeId in db.fetchAll(cmd, (self.teamId,self.teamId)):
            try:
                newGame = self.model.getById("games", gameId)
                homeTeam = self.model.getById("teams", homeId)
                awayTeam = self.model.getById("teams", awayId)
                newGame.setTeam("home", homeTeam)
                newGame.setTeam("away", awayTeam)
                games.append(newGame)
            except TypeError:
                pass
        return games


    def getLeagueStats(self, statType, stat):
        return self.model.getStats(statType, stat)


    def getLogoPath(self):
        raise AssertionError




################################################################################
################################################################################


class NBATeam(Team):

    def __init__(self, model, teamId):
        super().__init__(model, teamId)


    def getLogoPath(self):
        return logoPath.format("nba", self.teamId)


    def setInfo(self):
        db = self.model.getDB()
        self.info["league"] = "nba"
        self.info["firstName"], self.info["lastName"], self.info["abrv"] = db.fetchOne("SELECT first_name, last_name, abrv FROM pro_teams WHERE team_id = ?", (self.teamId,))
        self.info["colors"] = ["#"+x for x in db.fetchOne("SELECT primary_color, secondary_color FROM pro_teams WHERE team_id = ?", (self.teamId,))]


    def setStats(self):
        timeFrame = self.model.getTimeFrame()
        db = self.model.getDB()
        gdCmd = self.model.gdDict[timeFrame]

        teamStats = {}
        teamStats["all_results"] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"), db.fetchOne(SQL.teamResultStats.format({"gdCmd": gdCmd, "andJoinGD": ""}), (self.teamId,))))
        for hA in ("home", "away"):
            try:
                teamStats["{}_results".format(hA)] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"), db.fetchOne(SQL.teamResultStats.format({"gdCmd": gdCmd, "andJoinGD": "AND ts.team_id = gd.{}_id".format(hA)}), (self.teamId,))))
            except TypeError:
                teamStats["{}_results".format(hA)] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"),[0 for _ in range(len(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result")))]))

        for tO in ("team", "opp"):
            teamStats["all_{}".format(tO)] = dict(zip(("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.teamAvgStats.format({"gdCmd": gdCmd, "team": tO, "andJoinGD": ""}), (self.teamId,))))
            for hA in ("home", "away"):
                try:
                    teamStats["{}_{}".format(hA, tO)] = dict(zip(("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.teamAvgStats.format({"gdCmd": gdCmd, "team": tO, "andJoinGD": "AND ts.{}_id = gd.{}_id".format(tO, hA)}), (self.teamId,))))
                except TypeError:
                    teamStats["{}_{}".format(hA, tO)] = dict(zip(("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), [0 for _ in ("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls")]))

            for wL in ("winner", "loser"):
                try:
                    teamStats["{}_{}".format(wL, tO)] = dict(zip(("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.teamAvgStats.format({"gdCmd": gdCmd, "team": tO, "andJoinGD": "AND ts.{}_id = gd.{}_id".format(tO, wL)}), (self.teamId,))))
                except TypeError:
                    teamStats["{}_{}".format(wL, tO)] = dict(zip(("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), [0 for _ in ("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls")]))

            # teamStats["shots_{}".format(tO)] = {}
            # for box in range(1,11):
                # teamStats["shots_{}".format(tO)][box] = dict(zip(("fga", "fgm", "pts"), db.fetchOne(SQL.teamShotStats.format({"gdCmd": gdCmd, "team": tO}), (self.teamId, box))))
        self.stats[timeFrame] = teamStats

################################################################################
################################################################################


class NCAABTeam(Team):

    def __init__(self, model, teamId):
        super().__init__(model, teamId)


    def getLogoPath(self):
        return logoPath.format("ncaab", self.teamId)


    def setInfo(self):
        self.info["league"] = "ncaab"
        db = self.model.getDB()
        self.info["firstName"], self.info["lastName"], self.info["abrv"] = db.fetchOne("SELECT first_name, last_name, abrv FROM col_teams WHERE team_id = ?", (self.teamId,))
        # self.info["colors"] = ["#"+x for x in db.fetchOne("SELECT primary_color, secondary_color FROM pro_teams WHERE team_id = ?", (self.teamId,))]


    def setStats(self):
        timeFrame = self.model.getTimeFrame()
        db = self.model.getDB()
        gdCmd = self.model.gdDict[timeFrame]

        teamStats = {}
        try:
            teamStats["all_results"] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"), db.fetchOne(SQL.teamResultStats.format({"gdCmd": gdCmd, "andJoinGD": ""}), (self.teamId,))))
        except TypeError:
            teamStats["all_results"] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"),[0 for _ in range(len(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result")))]))

        for hA in ("home", "away"):
            try:
                teamStats["{}_results".format(hA)] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"), db.fetchOne(SQL.teamResultStats.format({"gdCmd": gdCmd, "andJoinGD": "AND ts.team_id = gd.{}_id".format(hA)}), (self.teamId,))))
            except TypeError:
                teamStats["{}_results".format(hA)] = dict(zip(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result"),[0 for _ in range(len(("wins", "loses", "atsWins", "atsLoses", "total", "money", "spread", "result")))]))

        for tO in ("team", "opp"):
            try:
                teamStats["all_{}".format(tO)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.colTeamAvgStats.format({"gdCmd": gdCmd, "team": tO, "andJoinGD": ""}), (self.teamId,))))
            except TypeError:
                teamStats["all_{}".format(tO)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), [0 for _ in ("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls")]))

            for hA in ("home", "away"):
                try:
                    teamStats["{}_{}".format(hA, tO)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.colTeamAvgStats.format({"gdCmd": gdCmd, "team": tO, "andJoinGD": "AND ts.{}_id = gd.{}_id".format(tO, hA)}), (self.teamId,))))
                except TypeError:
                    teamStats["{}_{}".format(hA, tO)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), [0 for _ in ("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls")]))

            for wL in ("winner", "loser"):
                try:
                    teamStats["{}_{}".format(wL, tO)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), db.fetchOne(SQL.colTeamAvgStats.format({"gdCmd": gdCmd, "team": tO, "andJoinGD": "AND ts.{}_id = gd.{}_id".format(tO, wL)}), (self.teamId,))))
                except TypeError:
                    teamStats["{}_{}".format(wL, tO)] = dict(zip(("fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls"), [0 for _ in ("b2b", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls")]))

            # teamStats["shots_{}".format(tO)] = {}
            # for box in range(1,11):
                # teamStats["shots_{}".format(tO)][box] = dict(zip(("fga", "fgm", "pts"), db.fetchOne(SQL.teamShotStats.format({"gdCmd": gdCmd, "team": tO}), (self.teamId, box))))
        self.stats[timeFrame] = teamStats
