from datetime import datetime, timedelta
from pprint import pprint
from re import sub
from sqlite3 import IntegrityError
from wx import Colour

from .FelsonCtrl import Model, Controller
from ..DB import NBADB, NBAMatchDB
from .. import Environ as ENV
from ..Views.FelsonFrame import NBAFrame


################################################################################
################################################################################


currentSeason = 2021
leagueId = "nba"
today = datetime.today()
yesterday = today-timedelta(1)


################################################################################
################################################################################


gameLogCmd = """
                SELECT DISTINCT game_date, (CASE WHEN gl.team_id = home_id THEN 1 ELSE 0 END),
                        gl.opp_id, team.pts, opp.pts, spread, money,
                        ou, spread_outcome, money_outcome, outcome
                    FROM game_lines AS gl

                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON gl.game_id = gd.game_id {0[andGL]} {0[andWGL]}
                    INNER JOIN ( SELECT ts.game_id, team_id, pts
                                    FROM team_stats AS ts
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ts.game_id = gd.game_id {0[andTS]} {0[andWL]}
                                        WHERE team_id = {0[teamId]}
                                    ) AS team
                        ON team.game_id = gl.game_id AND team.team_id = gl.team_id
                    INNER JOIN ( SELECT ts.game_id, opp_id, pts
                                    FROM team_stats AS ts
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ts.game_id = gd.game_id {0[oppTS]} {0[oppWL]}
                                        WHERE opp_id = {0[teamId]}
                                    ) AS opp
                        ON opp.game_id = gl.game_id AND opp.opp_id = gl.team_id
                    INNER JOIN over_unders AS ov
                        ON gl.game_id = ov.game_id
                    {0[whereGL]}
                    ORDER BY gl.game_id DESC
            """


injCmd = "SELECT first_name || ' ' || last_name || '   ' || abrv FROM players INNER JOIN position_types ON players.pos_id = position_types.pos_id WHERE player_id = ?"


class NBAModel(Model):

    _basePath = "/home/ededub/FEFelson/{}/{}/{}/{}/".format(leagueId, currentSeason, *str(today.date()).split("-")[1:])
    _db = NBADB
    _matchDB = NBAMatchDB
    _leagueId = leagueId
    _tFChoices = ENV.tFBasketballChoices

    def __init__(self):
        super().__init__()


    def newMatchDB(self, info):
        tables = ("game_lines", "over_unders", "games", "team_stats", "player_stats", "lineups", "player_shots")
        tables1 = ("over_unders", )


        t1Cmd = """
                SELECT *
                    FROM {} AS t1
                """

        glCmd = """
                SELECT team_id, opp_id, gl.game_id, spread, line, money, result, spread_outcome, money_outcome
                    FROM game_lines AS gl
                    INNER JOIN games
                    WHERE gl.game_id = games.game_id AND gl.team_id = games.home_id AND game_type = 'season'
                """


        cmd = """
                SELECT *
                    FROM {}
                    WHERE game_id = ?
                """


        allCmd = """
                    SELECT *
                        FROM players
                        WHERE player_id = ?
                """

        playerCmd = """
                    SELECT player_id
                        FROM player_stats AS ps
                        INNER JOIN games AS g
                            ON g.game_id = ps.game_id
                        WHERE season = {} AND home_id = ? OR away_id = ?
                    """.format(currentSeason)


        gCmd = """
                SELECT game_id
                    FROM games
                    WHERE season = {} AND (home_id = ? OR away_id = ?)
                """.format(currentSeason)





        self.matchDB.openDB()
        for team in ("away", "home"):
            teamId = info["{}Id".format(team)]
            games = [x[0] for x in self.db.fetchAll(gCmd, (teamId,teamId))]
            for gameId in games:
                for table in tables:
                    for item in self.db.fetchAll(cmd.format(table), (gameId, )):
                        try:
                            self.matchDB.insert(table, values=item)
                        except IntegrityError:
                            pass

            for playerId in [x[0] for x in self.db.fetchAll(playerCmd, (teamId,teamId))]:
                player = self.db.fetchOne(allCmd, (playerId,))
##                print(playerId, player)
                try:
                    self.matchDB.insert("players", values=player)
                except:
                    pass

        for table in tables1:
            for item in self.db.fetchAll(t1Cmd.format(table)):
                try:
                    self.matchDB.insert(table, values=item)
                except IntegrityError:
                    pass

        for item in self.db.fetchAll(glCmd):
            try:
                self.matchDB.insert("history_lines", values=item)
            except IntegrityError:
                pass



        self.matchDB.commit()
        self.matchDB.closeDB()


    def getBackgroundColor(self, hA, label, key, value, reverse):
        # print("hA "+hA, "label "+label, "key "+key)
        color = "white"
        colors = ["gold", "green", "pale green", "white", "pink", "red"]
        values = [x for x in range(1,7)]
        items = [x for x in range(1,6)]
        if reverse:
            values.reverse()
        labelColors = dict(zip(values, colors))
        # print("\n\ntO "+self.options["tO"], "reverse "+str(reverse), "stat "+key, "value "+str(value))
        # pprint(labelColors)
        # print("\n")
        hA = self.options["hA"] if self.options["hA"] == "all" else hA
        levels = self.report[label][self.options["tF"]][hA][key]

        # pprint(levels)
        try:
            for k in items:
                # print(value, levels[str(k)], value >= levels[str(k)])
                if value >= float(levels[str(k)]):
                    color = labelColors[k]
                    break
            if value < levels["5"]:
                color = labelColors[6]
        except TypeError:
            pass
        # print(color, "\n\n\n\n")
        return color

################################################################################
################################################################################


class NBACtrl(Controller):

    _frame = NBAFrame
    _gameLogCmd = gameLogCmd
    _injCmd = injCmd
    _model = NBAModel


    def __init__(self):
        super().__init__()


    def setTitle(self):
        super().setTitle()
        # print("\nnbactrl setTitle")

        b2bCmd = """
                SELECT game_id
                    FROM games
                    WHERE (home_id = ? OR away_id = ?) AND game_year = ? AND game_date = ?
                """

        recordCmd = """
                    SELECT IFNULL(SUM((CASE WHEN team_id = winner_id THEN 1 ELSE 0 END)), 0) AS wins,
                            IFNULL(SUM((CASE WHEN team_id = loser_id THEN 1 ELSE 0 END)), 0) AS loses
                        FROM game_lines AS gl
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON gl.game_id = gd.game_id {0[andGL]} {0[andWGL]}
                        WHERE team_id = ? {0[whereGL]}
                    """

        gdCmd = self.model.getGDCmd()


        for hA in ("away", "home"):
            teamId = self.model.getGame()["{}Id".format(hA)]
            whereGL = sub("WHERE", "AND", self.model.getWhereGLCmd(hA))
            andGL = self.model.getAndGLCmd(hA)
            andWGL = self.model.getAndWGLCmd(hA)

            # print(recordCmd.format({"gdCmd":gdCmd, "andWGL":andWGL, "andGL": andGL, "whereGL":whereGL}))
            self.model.matchDB.openDB()
            record = self.model.matchDB.fetchOne(recordCmd.format({"gdCmd":gdCmd, "andWGL":andWGL, "andGL": andGL, "whereGL":whereGL}), (teamId,))
            self.frame.titlePanel.values[hA]["record"].SetLabel("{} - {}".format(*record))

            self.frame.titlePanel.values[hA]["b2b"].Hide()
            if self.model.matchDB.fetchItem(b2bCmd, (teamId, teamId, yesterday.year, "{}.{}".format(*str(yesterday.date()).split("-")[1:]))):
                print("set b2b tag")
                self.frame.titlePanel.values[hA]["b2b"].Show()
            self.model.matchDB.closeDB()
            self.frame.titlePanel.Layout()


    def setPlayerStats(self):
        statList = ("playerId", "name", "pos", "gp", "start%","fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts", "oreb",  "reb",
                    "ast", "stl", "blk", "trn", "fls", "mins", "plmn")

        cmd = """
                SELECT ts.player_id, first_name || ' ' || last_name, abrv, COUNT(ts.game_id), AVG(starter), AVG(fga), SUM(fgm)/(SUM(fga)*1.0), AVG(fta),
                        SUM(ftm)/(SUM(fta)*1.0), AVG(tpa), SUM(tpm)/(SUM(tpa)*1.0), AVG(pts),
                        AVG(oreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn),
                        AVG(fls), AVG(mins), AVG(plmn)
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN player_stats AS ts
                        ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                    INNER JOIN players
                        ON ts.player_id = players.player_id
                    INNER JOIN lineups
                        ON ts.game_id = lineups.game_id AND ts.player_id = lineups.player_id AND ts.team_id = lineups.team_id
                    INNER JOIN position_types AS pt
                        ON players.pos_id = pt.pos_id
                    WHERE ts.{0[team]}_id = ? {0[whereTS]}
                    GROUP BY ts.player_id, ts.{0[team]}_id
                    HAVING AVG(mins) > 0
                    ORDER BY AVG(pts) DESC
                    LIMIT 10
            """

        gdCmd = self.model.getGDCmd()
        for hA in ("away", "home"):
            reverse = False
            teamId = self.model.getGame()["{}Id".format(hA)]
            andTS = self.model.getAndTSCmd(hA)
            andWL = self.model.getAndWLCmd(hA)
            whereTS = sub("WHERE", "AND", self.model.getWhereTSCmd(hA))

            self.model.matchDB.openDB()
            for i, player in enumerate([dict(zip(statList, player)) for player in self.model.matchDB.fetchAll(cmd.format({"gdCmd":gdCmd, "andTS":andTS, "andWL":andWL, "whereTS":whereTS, "team":self.model.options["tO"]}), (teamId,))]):

                for key in ("name", "pos", "gp","start%","fg%", "ft%", "tp%", "pts", "oreb",  "reb",
                    "ast", "stl", "blk", "trn", "fls", "mins", "plmn"):

                    try:
                        if key in ("fg%", "ft%", "tp%", "start%"):
                            text = "{:.0f}%".format(player[key]*100)
                        elif key in ("name", "pos"):
                            if player[key]:
                                text = player[key]
                            else:
                                text = "n/a"
                        elif key in ("pts", "trn", "fls", "plmn",):
                            text = "{:.1f}".format(player[key])
                        else:
                            text = "{:.0f}".format(player[key])
                    except:
                        text = "--"

                    self.frame.panels["Player Stats"].values[hA][i][key].SetLabel(text)
                    if self.model.options["tO"] == "team":
                        reverse = True if key in ("trn", "fls", ) else False
                    if key not in ("name", "mins", "gp", "start%", "pos"):
                        color = self.model.getBackgroundColor(hA, "playerStats", key, player[key], reverse)
                        textColor = "black"
                        if color in ('green', 'red'):
                            textColor = "white"

                        self.frame.panels["Player Stats"].values[hA][i][key].SetBackgroundColour(color)
                        self.frame.panels["Player Stats"].values[hA][i][key].SetForegroundColour(Colour(textColor))
            self.model.matchDB.closeDB()
        self.frame.panels["Player Stats"].Layout()


    def setTeamStats(self):

        teamStatList = ("fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts", "oreb", "dreb", "reb",
                            "ast", "stl", "blk", "trn", "fls", "pts_in_pt", "fb_pts")
        cmd = """
                    SELECT AVG(fga), SUM(fgm)/(SUM(fga)*1.0), AVG(fta),
                            SUM(ftm)/(SUM(fta)*1.0), AVG(tpa), SUM(tpm)/(SUM(tpa)*1.0), AVG(pts),
                            AVG(oreb), AVG(dreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn),
                            AVG(fls), AVG(pts_in_pt), AVG(fb_pts)
                        FROM ( {0[gdCmd]} ) AS gd
                        INNER JOIN team_stats AS ts
                            ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                        WHERE ts.{0[team]}_id = ? {0[whereTS]}
                """


        gdCmd = self.model.getGDCmd()
        for hA in ("away", "home"):
            reverse = False
            teamId = self.model.getGame()["{}Id".format(hA)]
            andTS = self.model.getAndTSCmd(hA)
            andWL = self.model.getAndWLCmd(hA)
            whereTS = sub("WHERE", "AND", self.model.getWhereTSCmd(hA))
            self.model.matchDB.openDB()
            stats = dict(zip(teamStatList, self.model.matchDB.fetchOne(cmd.format({"gdCmd":gdCmd, "andTS":andTS, "andWL":andWL, "team": self.model.options["tO"], "whereTS":whereTS}), (teamId,))))
            self.model.matchDB.closeDB()
            for key, value in stats.items():
                try:
                    if key in ("fg%", "ft%", "tp%"):
                        text = "{:.0f}%".format(value*100)
                    elif key in ("pts", "trn", "fls"):
                        text = "{:.1f}".format(value)
                    else:
                        text = "{:.0f}".format(value)
                except:
                    text = "--"
                self.frame.panels["Team Stats"].values[hA][key].SetLabel(text)
                if self.model.options["tO"] == "team":
                    reverse = True if key in ("trn", "fls", ) else False
                else:
                    reverse = False if key in ("trn", "fls", ) else True

                color = self.model.getBackgroundColor(hA, "teamStats", key, value, reverse)
                textColor = "black"
                if color in ('green', 'red'):
                    textColor = "white"
                self.frame.panels["Team Stats"].values[hA][key].SetBackgroundColour(Colour(color))
                self.frame.panels["Team Stats"].values[hA][key].SetForegroundColour(Colour(textColor))

        self.frame.panels["Team Stats"].Layout()
