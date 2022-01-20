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


    def getCommonOpp(self, hA):
        timeFrame = self.model.getTimeFrame()
        db = self.model.getDB()
        gdCmd = self.model.gdDict[timeFrame]

        if hA == "all":
            homeCmd = SQL.oppCmd.format({"gdCmd": gdCmd, "oppAndCmd": "", "teamId": self.teams["home"].getId()})
            awayCmd = SQL.oppCmd.format({"gdCmd": gdCmd, "oppAndCmd": "", "teamId": self.teams["away"].getId()})
        else:
            homeCmd = SQL.oppCmd.format({"gdCmd": gdCmd, "oppAndCmd": " AND gd.home_id ="+str(self.teams["home"].getId()), "teamId": self.teams["home"].getId()})
            awayCmd = SQL.oppCmd.format({"gdCmd": gdCmd, "oppAndCmd": " AND gd.away_id ="+str(self.teams["away"].getId()), "teamId": self.teams["away"].getId()})

        cmd = SQL.commOppCmd.format({"oppHome": homeCmd, "oppAway": awayCmd})
        return db.fetchAll(cmd)


    def getCommonStats(self, hA):
        comOpps = [x[0] for x in self.getCommonOpp(hA)]
        teamStats = {}
        for homeA in ("away", "home"):
            if hA == "all":
                teamStats[homeA] = self.getCommonTeamStats("all", self.teams[homeA].getId(), comOpps)
            else:
                teamStats[homeA] = self.getCommonTeamStats(homeA, self.teams[homeA].getId(), comOpps)
        return teamStats


    def getCommonTeamStats(self, hA, teamId, comOpps):
        timeFrame = self.model.getTimeFrame()
        db = self.model.getDB()
        gdCmd = self.model.gdDict[timeFrame]
        statAbrvs = ("pts", "fga", "fgPct", "fta", "ftPct", "tpa", "tpPct", "reb", "oreb", "ast", "stl", "blk", "trn", "fls")

        teamStats = {}

        teamCmd = ""
        oppCmd = ""
        hAOpp = ""
        try:
            commCmd = "IN "+str(tuple(comOpps)) if len(comOpps) > 1 else "= "+str(comOpps[0])
        except IndexError:
            commCmd = "= -1"


        if hA != "all":
            hAOpp = "away" if hA == "home" else "home"

        #### teamStats vs Common opps
        if hA == "all":
            teamCmd = "ts.team_id = "+str(teamId)
            oppCmd = "ts.opp_id "+commCmd
        else:
            teamCmd = "ts.team_id = "+str(teamId)+" AND ts.team_id = gd.{}_id".format(hA)
            oppCmd = "ts.opp_id "+commCmd + " AND ts.opp_id = gd.{}_id".format(hAOpp)

        teamStats["team"] = dict(zip(statAbrvs, db.fetchOne(SQL.commStatsCmd.format({"gdCmd": gdCmd, "teamCmd": teamCmd, "oppCmd": oppCmd }))))

        #### teamStats vs Every Other team
        if hA == "all":
            teamCmd = "ts.opp_id != "+str(teamId)
            oppCmd = "ts.team_id "+commCmd
        else:
            teamCmd = "ts.opp_id != "+str(teamId)+" AND ts.opp_id = gd.{}_id".format(hA)
            oppCmd = "ts.team_id "+commCmd + " AND ts.team_id = gd.{}_id".format(hAOpp)

        teamStats["teamBase"] = dict(zip(statAbrvs, db.fetchOne(SQL.commStatsCmd.format({"gdCmd": gdCmd, "teamCmd": teamCmd, "oppCmd": oppCmd }))))

        #### comOppStats vs team
        if hA == "all":
            teamCmd = "ts.team_id "+ commCmd
            oppCmd = "ts.opp_id = "+str(teamId)
        else:
            teamCmd = "ts.team_id "+commCmd + " AND ts.team_id = gd.{}_id".format(hAOpp)
            oppCmd = "ts.opp_id = "+str(teamId)+" AND ts.opp_id = gd.{}_id".format(hA)

        teamStats["opp"] = dict(zip(statAbrvs, db.fetchOne(SQL.commStatsCmd.format({"gdCmd": gdCmd, "teamCmd": teamCmd, "oppCmd": oppCmd }))))


        #### comOppStats vs Every Other team
        if hA == "all":
            teamCmd = "ts.opp_id "+commCmd
            oppCmd = "ts.team_id != "+str(teamId)
        else:
            teamCmd = "ts.opp_id "+commCmd + " AND ts.opp_id = gd.{}_id".format(hAOpp)
            oppCmd = "ts.team_id != "+str(teamId)+" AND ts.team_id = gd.{}_id".format(hA)

        teamStats["oppBase"] = dict(zip(statAbrvs, db.fetchOne(SQL.commStatsCmd.format({"gdCmd": gdCmd, "teamCmd": teamCmd, "oppCmd": oppCmd }))))

        return teamStats




    def getPlayerStats(self, playerId, label):
        return self.playerStats[playerId][label]


    def getMatchups(self):
        db = self.model.getDB()
        return db.fetchAll(SQL.matchupResultCmd, (self.teams["home"].getId(),self.teams["away"].getId()))


    def getLeagueStats(self, statType, stat):
        return self.model.getStats(statType, stat)


    def getTeam(self, hA):
        return self.teams[hA]


    def getTimeFrame(self):
        return self.model.getTimeFrame()


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
