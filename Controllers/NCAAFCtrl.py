from datetime import datetime, timedelta
from pprint import pprint
from re import sub
from sqlite3 import IntegrityError
from wx import Colour

from .FelsonCtrl import Model, Controller
from ..DB import NCAAFDB, NCAAFMatchDB
from .. import Environ as ENV
from ..Views.FelsonFrame import NCAAFFrame

################################################################################
################################################################################

currentSeason = 2021
currentWeek = 15
leagueId = "ncaaf"

################################################################################
################################################################################

gameLogCmd = """
                SELECT DISTINCT game_date, (CASE WHEN gl.team_id = home_id THEN 1 ELSE 0 END),
                        gl.opp_id, team.pts, opp.pts, spread, money,
                        ou, spread_outcome, money_outcome, outcome
                    FROM game_lines AS gl

                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON gl.game_id = gd.game_id {0[andGL]} {0[andWGL]}
                    INNER JOIN ( SELECT ts.game_id, team_id, value AS pts
                                    FROM team_stats AS ts
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ts.game_id = gd.game_id {0[andTS]} {0[andWL]}
                                        WHERE stat_id = 963 AND team_id = {0[teamId]}
                                    ) AS team
                        ON team.game_id = gl.game_id AND team.team_id = gl.team_id
                    INNER JOIN ( SELECT ts.game_id, opp_id, value AS pts
                                    FROM team_stats AS ts
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ts.game_id = gd.game_id {0[oppTS]} {0[oppWL]}
                                        WHERE stat_id = 963 AND opp_id = {0[teamId]}
                                    ) AS opp
                        ON opp.game_id = gl.game_id AND opp.opp_id = gl.team_id
                    INNER JOIN over_unders AS ov
                        ON gl.game_id = ov.game_id
                    {0[whereGL]}
                    ORDER BY gl.game_id DESC
            """


injCmd = "SELECT first_name || ' ' || last_name || '   ' || abrv FROM players INNER JOIN positions ON players.pos_id = positions.pos_id WHERE player_id = ?"


class NCAAFModel(Model):

    _db = NFLDB
    _matchDB = NCAAFMatchDB
    _leagueId = leagueId
    _tFChoices = ENV.tFFootballChoices
    _basePath = "/home/ededub/FEFelson/{}/{}/{}/".format(leagueId, currentSeason, currentWeek)


    def __init__(self):
        super().__init__()


    def getBackgroundColor(self, hA, label, key, value, reverse):
        color = "WHITE"
        colors = ["red", "pink", "white", "pale green", "green", "gold"]
        values = [x for x in range(1,7)]
        items = [x for x in range(1,6)]
        if reverse:
            values.reverse()
            items.reverse()
        labelColors = dict(zip(values, colors))
        # print("\n\ntO "+self.options["tO"], "reverse "+str(reverse), "stat "+key, "value "+str(value))
        # pprint(labelColors)
        # print("\n")
        hA = self.options["hA"] if self.options["hA"] == "all" else hA

        # pprint(levels)
        try:
            levels = self.report[label][self.options["tF"]][hA][key]
            if reverse:
                for k in items:
                    if value <= levels[str(k)]:
                        color = labelColors[k]
                    else:
                        break
                if value > levels["5"]:
                    color = labelColors[6]
            else:
                for k in items:
                    if value >= levels[str(k)]:
                        color = labelColors[k]
                    else:
                        break
                if value > levels["5"]:
                    color = labelColors[6]
        except (TypeError, KeyError):
            pass
        # print(color, "\n\n\n\n")
        return Colour(color)


    def getBackgroundColor1(self, hA, label, label1, stat, value, reverse):
        color = "WHITE"
        colors = ["red", "pink", "white", "pale green", "green", "gold"]
        values = [x for x in range(1,7)]
        items = [x for x in range(1,6)]
        if reverse:
            values.reverse()
            items.reverse()
        labelColors = dict(zip(values, colors))
        # print("\n\ntO "+self.options["tO"], "reverse "+str(reverse), "stat "+key, "value "+str(value))
        # pprint(labelColors)
        # print("\n")
        hA = self.options["hA"] if self.options["hA"] == "all" else hA


        # pprint(levels)
        try:
            levels = self.report[label][label1][self.options["tF"]][hA][stat]
            # pprint(levels)
            # raise
            if reverse:
                for k in items:
                    if value <= levels[str(k)]:
                        color = labelColors[k]
                    else:
                        break
                if value > levels["5"]:
                    color = labelColors[6]
            else:
                for k in items:
                    if value >= levels[str(k)]:
                        color = labelColors[k]
                    else:
                        break
                if value > levels["5"]:
                    color = labelColors[6]
        except (TypeError, KeyError):
            pass
        # print(color, "\n\n\n\n")
        return Colour(color)


    def newMatchDB(self, info):
        tables = ("game_lines", "over_unders", "games", "team_stats", "player_stats", "lineups", )

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

        self.matchDB.commit()
        self.matchDB.closeDB()


################################################################################
################################################################################


class NCAAFCtrl(Controller):

    _frame = NCAFFFrame
    _gameLogCmd = gameLogCmd
    _injCmd = injCmd
    _model = NCAAFModel


    def __init__(self):
        super().__init__()


    def setTitle(self):
        super().setTitle()
        print("\nncaafctrl setTitle")


        recordCmd = """
                    SELECT IFNULL(SUM((CASE WHEN team_id = winner_id THEN 1 ELSE 0 END)),0) AS wins,
                            IFNULL(SUM((CASE WHEN team_id = loser_id THEN 1 ELSE 0 END)),0) AS loses,
                            IFNULL(SUM((CASE WHEN winner_id = -1 THEN 1 ELSE 0 END)), 0) AS tied
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
            self.model.matchDB.closeDB()
            self.frame.titlePanel.values[hA]["record"].SetLabel("{} - {} - {}".format(*record))


    def setPlayerStats(self):
        playerPassList = ("playerId", "name", "pos", "att", "comp%", "yds", "avg", "td", "int", "rating")
        playerRushList = ("playerId", "name", "pos", "car", "yds", "avg", "td", "fum")
        playerRecList = ("playerId", "name", "pos", "tgt", "rec", "yds", "avg", "td", "fum")

        passingCmd = """
                        SELECT lineups.player_id, first_name || ' ' || last_name, abrv, att.value, comp.value/att.value,
                                yds.value, yds.value/comp.value, tds.value, ints.value, rating.value
                            FROM lineups
                            INNER JOIN players
                                ON lineups.player_id = players.player_id
                            INNER JOIN positions AS pt
                                ON players.pos_id = pt.pos_id
                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 102 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS comp
                                ON lineups.team_id = comp.team_id AND lineups.player_id = comp.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 103 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS att
                                ON lineups.team_id = att.team_id AND lineups.player_id = att.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 105 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS yds
                                ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 108 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS tds
                                ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id


                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 109 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS ints
                                ON lineups.team_id = ints.team_id AND lineups.player_id = ints.player_id


                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 113 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS rating
                                ON lineups.team_id = rating.team_id AND lineups.player_id = rating.player_id

                            GROUP BY lineups.player_id
                            ORDER BY att.value DESC
                            LIMIT 2

            """

        rushingCmd = """
                        SELECT lineups.player_id, first_name || ' ' || last_name, abrv, att.value, yds.value,
                                yds.value/att.value, tds.value, fum.value
                            FROM lineups
                            INNER JOIN players
                                ON lineups.player_id = players.player_id
                            INNER JOIN positions AS pt
                                ON players.pos_id = pt.pos_id
                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 202 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS att
                                ON lineups.team_id = att.team_id AND lineups.player_id = att.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 203 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS yds
                                ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 207 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS tds
                                ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id


                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 3 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS fum
                                ON lineups.team_id = fum.team_id AND lineups.player_id = fum.player_id


                            GROUP BY lineups.player_id
                            ORDER BY att.value DESC
                            LIMIT 4

            """


        receivingCmd = """
                        SELECT lineups.player_id, first_name || ' ' || last_name, abrv, tgt.value, rec.value, yds.value,
                                yds.value/rec.value, tds.value, fum.value
                            FROM lineups
                            INNER JOIN players
                                ON lineups.player_id = players.player_id
                            INNER JOIN positions AS pt
                                ON players.pos_id = pt.pos_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 310 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS tgt
                                ON lineups.team_id = tgt.team_id AND lineups.player_id = tgt.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 302 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS rec
                                ON lineups.team_id = rec.team_id AND lineups.player_id = rec.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 303 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS yds
                                ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 309 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS tds
                                ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id

                            INNER JOIN (
                                        SELECT team_id, player_id, AVG(value) AS value
                                            FROM ( {0[gdCmd]} ) AS gd
                                            INNER JOIN player_stats AS ts
                                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                                            WHERE stat_id = 3 AND team_id = {0[teamId]}
                                            GROUP BY player_id
                                        ) AS fum
                                ON lineups.team_id = fum.team_id AND lineups.player_id = fum.player_id



                            GROUP BY lineups.player_id
                            ORDER BY tgt.value DESC
                            LIMIT 7

            """

        reverse = False
        gdCmd = self.model.getGDCmd()

        for hA in ("away", "home"):
            teamId = self.model.getGame()["{}Id".format(hA)]
            whereTS = sub("WHERE", "AND", self.model.getWhereGLCmd(hA))
            andTS = self.model.getAndTSCmd(hA)
            andWL = self.model.getAndWLCmd(hA)

            for label in ("passing", "rushing", "receiving"):
                statList, cmd = {"passing":(playerPassList, passingCmd), "rushing": (playerRushList, rushingCmd), "receiving":(playerRecList, receivingCmd)}[label]

                self.model.matchDB.openDB()
                for i, player in  enumerate(self.model.matchDB.fetchAll(cmd.format({"gdCmd":gdCmd, "andTS":andTS, "andWL":andWL, "teamId": teamId}))):
                    player = dict(zip(statList,player))
                    # pprint(player)
                    for stat in statList:
                        if stat != "playerId":

                            try:
                                if stat in ("comp%",):
                                    text = "{:.0f}%".format(player[stat]*100)
                                elif stat in ("avg", "td", "int", "fum"):
                                    text = "{:.1f}".format(player[stat])
                                elif stat in ("name", "pos"):
                                    text = "{}".format(player[stat])
                                else:
                                    text = "{:.0f}".format(player[stat])
                            except:
                                text = "--"

                            self.frame.panels["Player Stats"].values[hA][label][i][stat].SetLabel(text)

                            if self.model.options["tO"] == "team":
                                reverse = True if stat in ("int", "fum") else False
                            else:
                                reverse = False if stat in ("int", "fum") else True
                            if stat not in ("playerId", "name", "pos"):
                                self.frame.panels["Player Stats"].values[hA][label][i][stat].SetBackgroundColour(self.model.getBackgroundColor1(hA, "playerStats", label, stat, player[stat], reverse))

                self.model.matchDB.closeDB()
        self.frame.panels["Player Stats"].Layout()


    def setTeamStats(self):

        teamStats = ("PLAYS", "Points", "TmPaAtt", "TmPaComp", "TmPaYds", "PaAvg", "PaTDs",
                "TmINTS", "TmRuAtt", "TmRuYds", "RuAvg", "RuTDs", "TmFum", "TO",
                "PEN", "PENYds", "POSSTIME", "TmPaSACKS", "TmPaSACKYds", "3DAtt", "4DAtt", "3DComp", "4DComp",
                "TmYDS",)

        teamStats1 = ("PLAYS", "Points", "TmPaAtt", "TmPaComp", "TmPaYds", "PaAvg", "PaTDs",
                    "TmINTS", "TmRuAtt", "TmRuYds", "RuAvg", "RuTDs", "TmFum", "TO",
                    "PEN", "PENYds", "POSSTIME", "TmPaSACKS", "TmPaSACKYds", "3rd%", "4th%", "TmYDS",)


        teamStatCmd = """
                        SELECT AVG(value)
                            FROM team_stats AS ts
                            INNER JOIN ( {0[gdCmd]} ) AS gd
                                ON ts.game_id = gd.game_id {0[andTS]} {0[andWL]}
                            INNER JOIN stat_types AS st
                                ON ts.stat_id = st.stat_id
                            WHERE st.abrv = ? AND {0[team]}_id = ? {0[whereTS]}
                        """


        playerStatCmd = """
                        SELECT AVG(value)
                            FROM (SELECT SUM(value) AS value, team_id
                                        FROM player_stats AS ts
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ts.game_id = gd.game_id {0[andTS]} {0[andWL]}
                                        INNER JOIN stat_types AS st
                                            ON ts.stat_id = st.stat_id
                                        WHERE st.abrv = ?
                                        GROUP BY ts.game_id, team_id)
                            WHERE team_id = ? {0[whereTS]}
                        """

        reverse = False
        gdCmd = self.model.getGDCmd()

        for hA in ("away", "home"):
            teamId = self.model.getGame()["{}Id".format(hA)]
            whereTS = sub("WHERE", "AND", self.model.getWhereGLCmd(hA))
            andTS = self.model.getAndTSCmd(hA)
            andWL = self.model.getAndWLCmd(hA)

            info = {}
            for stat in teamStats:

                if stat in ("PaTDs", "RuTDs"):
                    cmd = playerStatCmd
                else:
                    cmd = teamStatCmd

                self.model.matchDB.openDB()
                info[stat] = self.model.matchDB.fetchItem(cmd.format({"gdCmd":gdCmd, "andTS":andTS, "andWL":andWL, "whereTS":whereTS, "team": self.model.options["tO"]}), (stat, teamId))
                self.model.matchDB.closeDB()

            for stat in teamStats1:

                try:
                    if stat not in ("3rd%", "4th%", "RuAvg", "PaAvg",):
                        value = info[stat]
                    elif stat == "3rd%":
                        value = (info["3DComp"]/info["3DAtt"])*100
                    elif stat == "4th%":
                        value = (info["4DComp"]/info["4DAtt"])*100
                    elif stat == "PaAvg":
                        value = (info["TmPaYds"]/info["TmPaComp"])
                except:
                    value = None

                try:
                    if stat in ("TmPaAtt", "TmPaComp", "TmRuAtt", "PLAYS", "TmPaYds", "TmRuYds", "TmYDS", "3rd%", "4th%"):
                        label = "{:.0f}".format(value)
                    else:
                        label = "{:.1f}".format(value)
                except:
                    label = "--"

                self.frame.panels["Team Stats"].values[hA][stat].SetLabel(label)

                if self.model.options["tO"] == "team":
                    reverse = True if stat in ("PEN", "PENYds", "TmPaSACKS", "TmPaSACKYds", "TmFum", "TO", "TmINTS") else False
                else:
                    reverse = False if stat in ("PEN", "PENYds", "TmPaSACKS", "TmPaSACKYds", "TmFum", "TO", "TmINTS") else True

                self.frame.panels["Team Stats"].values[hA][stat].SetBackgroundColour(self.model.getBackgroundColor(hA, "teamStats", stat, value, reverse))

        self.frame.panels["Team Stats"].Layout()
