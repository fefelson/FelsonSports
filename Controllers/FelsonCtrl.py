import datetime
import json
import os
import wx

from .. import Environ as ENV

from abc import ABCMeta, abstractmethod
from pprint import pprint
from re import search, sub

from ..Utils.SQL import getGDCmds


################################################################################
################################################################################


today = datetime.date.today()


matchPath = ".db/M{0[gameId]}.db"
reportPath = "/home/ededub/FEFelson/{0[leagueId]}/.report.json"


################################################################################
################################################################################


class Model(metaclass=ABCMeta):

    _basePath = None
    _db = None
    _matchDB = None
    _leagueId = None
    _tFChoices = None
    _options = {"tF":None, "hA":None, "tO":None, "wL":None, "comm":None, "vs":None}

    def __init__(self):

        self.db = self._db()
        self.games = {}
        self.curGame = None
        self.matchDB = None
        self.leagueId = self._leagueId
        self.options = self._options.copy()

        self.setDefaultOptions()
        self.gdCmds = getGDCmds(2021)
        self.db.openDB()

        with open(reportPath.format({"leagueId":self.leagueId})) as reportIn:
            self.report = json.load(reportIn)

        for fileName in [self._basePath.format({"leagueId":self.leagueId}) +fileName for fileName in os.listdir(self._basePath.format({"leagueId":self._leagueId})) if fileName[0] == "M"]:
            with open(fileName) as fileIn:
                info = json.load(fileIn)

            if datetime.datetime.strptime(info["gameTime"], "%a, %d %b %Y %H:%M:%S %z").timestamp() > datetime.datetime.now().timestamp():
                self.games[info["gameId"]] = info


                if not os.path.exists(self._basePath+matchPath.format(info)):
                    self.matchDB = self._matchDB(self._basePath+matchPath.format(info))
                    self.newMatchDB(info)

        self.db.closeDB()


    @abstractmethod
    def newMatchDB(self, info):
        pass


    def getAndGLCmd(self, awayHome):
        # print("\nmodel getAndGLCmd")
        andGL = "" if self.options["hA"] == "all" else "AND gd.{}_id = gl.{}_id".format(awayHome, self.options["tO"])
        # print(andGL)
        return andGL


    def getAndTSCmd(self, awayHome):
        # print("\nmodel getAndTSCmd")
        andTS = "" if self.options["hA"] == "all" else "AND gd.{}_id = ts.{}_id".format(awayHome, self.options["tO"])
        # print(andTS)
        return andTS


    def getAndWLCmd(self, awayHome):
        # print("\nmodel getAndWLCmd")
        andWL = "" if self.options["wL"] == "all" else "AND gd.{}_id = ts.{}_id".format(self.options["wL"], self.options["tO"])
        # print(andWL)
        return andWL


    def getAndWGLCmd(self, awayHome):
        # print("\nmodel getAndWGLCmd")
        andWGL = "" if self.options["wL"] == "all" else "AND gd.{}_id = gl.{}_id".format(self.options["wL"], self.options["tO"])
        # print(andWGL)
        return andWGL


    @abstractmethod
    def getBackgroundColor(self, key, stat, reverse):
        pass


    def getCommonOpps(self, awayHome):
        info = self.getGame()
        gdCmd = self.getGDCmd()
        andTS = self.getAndTSCmd(awayHome)
        andWL = self.getAndWLCmd(awayHome)
        cmd = """
                SELECT DISTINCT opp_id
                    FROM ( {0[gdCmd]} ) AS gd
                            INNER JOIN team_stats AS ts
                                ON gd.game_id = ts.game_id {0[andTS]} {0[andWL]}
                    WHERE team_id = ?
                """

        self.matchDB.openDB()
        home = [x[0] for x in self.matchDB.fetchAll(cmd.format({"gdCmd":gdCmd, "andTS":andTS, "andWL":andWL}), (info["homeId"],) )]
        away = [x[0] for x in self.matchDB.fetchAll(cmd.format({"gdCmd":gdCmd, "andTS":andTS, "andWL":andWL}), (info["awayId"],) )]
        self.matchDB.closeDB()
        opps = set(home) & set(away)
        # print(opps)
        return list(opps)


    def getGame(self):
        return self.games[self.curGame]


    def getGDCmd(self):
        return self.gdCmds[self.options["tF"]]


    def getWhereGLCmd(self, awayHome):
        # print("\nmodel getWhereGLCmd")
        whereGLCmd = ""
        oppTO = "opp" if self.options["tO"] == "team" else "team"
        if self.options["comm"] or self.options["vs"]:
            if self.options["comm"]:
                opponents = self.getCommonOpps(awayHome)
            else:
                info = self.getGame()
                opponents = (info["awayId"],) if awayHome == "home" else (info["homeId"],)

            if len(opponents) == 1:
                whereGLCmd = "WHERE gl.{}_id = {}".format(oppTO, opponents[0])
            elif len(opponents) > 1:
                whereGLCmd = "WHERE gl.{}_id IN {}".format(oppTO, str(tuple(opponents)))
            else:
                whereGLCmd = "WHERE gl.{}_id = -1".format(oppTO)
        # print(whereGLCmd)
        return whereGLCmd


    def getWhereTSCmd(self, awayHome):
        # print("\nmodel getWhereGLCmd")
        whereTSCmd = ""
        oppTO = "opp" if self.options["tO"] == "team" else "team"
        if self.options["comm"] or self.options["vs"]:
            if self.options["comm"]:
                opponents = self.getCommonOpps(awayHome)
            else:
                info = self.getGame()
                opponents = (info["awayId"],) if awayHome == "home" else (info["homeId"],)

            if len(opponents) == 1:
                whereTSCmd = "WHERE ts.{}_id = {}".format(oppTO, opponents[0])
            elif len(opponents) > 1:
                whereTSCmd = "WHERE ts.{}_id IN {}".format(oppTO, str(tuple(opponents)))
            else:
                whereTSCmd = "WHERE ts.{}_id = -1".format(oppTO)
        # print(whereGLCmd)
        return whereTSCmd


    def setDefaultOptions(self):
        self.options = {"tF":self._tFChoices[0], "hA":"all", "tO":"team", "wL":"all", "comm":False, "vs":False}


    def setGame(self, gameId):
        if gameId in self.games.keys():
            self.curGame = gameId
        self.matchDB = self._matchDB(self._basePath+matchPath.format({"gameId":gameId, "leagueId":self._leagueId}))


    def setOption(self, key, value):
        # print("\nmodel setOption", "key {}".format(key), "value {}".format(value))
        # print("old Options")
        # pprint(self.options)
        self.options[key] = value
        # print("\nnew options")
        # pprint(self.options)


################################################################################
################################################################################


class Controller(metaclass=ABCMeta):

    _frame = None
    _gameLogCmd = None
    _injCmd = None
    _model = None


    def __init__(self):

        self.model = self._model()
        self.frame = self._frame(None)
        self.frame.options["tF"].Bind(wx.EVT_COMBOBOX, self.changeOption)
        self.frame.options["hA"].Bind(wx.EVT_RADIOBOX, self.changeOption)
        self.frame.options["tO"].Bind(wx.EVT_RADIOBOX, self.changeOption)
        self.frame.options["wL"].Bind(wx.EVT_RADIOBOX, self.changeOption)
        self.frame.options["comm"].Bind(wx.EVT_CHECKBOX, self.changeOpponents)
        self.frame.options["vs"].Bind(wx.EVT_CHECKBOX, self.changeOpponents)

        for game in sorted(self.model.games.values(), key=lambda x: datetime.datetime.strptime(x["gameTime"], "%a, %d %b %Y %H:%M:%S %z")):
            self.frame.listPanel.addGame(game, self.changeGame)

        self.frame.Show()


    def changeGame(self, event):
        gameId = event.GetEventObject().GetName()
        self.model.setGame(gameId)
        self.model.setDefaultOptions()
        self.setFrameOptions()
        self.changeFrame()
        print(gameId)


    def changeOpponents(self, event):
        box = event.GetEventObject()
        value = box.GetName()
        if box.GetValue():
            if value == "vs":
                self.model.setOption("comm", False)
                self.frame.options["comm"].SetValue(False)
            else:
                self.model.setOption("vs", False)
                self.frame.options["vs"].SetValue(False)

        self.model.setOption(value, box.GetValue())
        self.changeFrame()


    def changeOption(self, event):
        # print("\nctrl changeOption")
        obj = event.GetEventObject()
        name = obj.GetName()
        value = None

        if name == "tF":
            value = obj.GetString(obj.GetCurrentSelection())
        else:
            value = obj.GetString(obj.GetSelection())

        self.model.setOption(name, value)
        self.changeFrame()


    def setFrameOptions(self):
        self.frame.options["tF"].SetSelection(0)
        self.frame.options["hA"].SetSelection(0)
        self.frame.options["tO"].SetSelection(0)
        self.frame.options["wL"].SetSelection(0)
        self.frame.options["comm"].SetValue(False)
        self.frame.options["vs"].SetValue(False)


    def changeFrame(self):
        print("\nctrl changeFrame")
        self.frame.panels['Game Log'].DestroyChildren()
        self.frame.panels['Injuries'].DestroyChildren()

        self.setTitle()
        self.setTeamStats()
        self.setInjuries()
        self.setPlayerStats()
        self.setGameLog()
        self.setGameLine()
        self.setGaming()
        self.frame.Layout()


    @abstractmethod
    def setTitle(self):
        info = self.model.getGame()
        gd = datetime.datetime.strptime(info["gameTime"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)
        self.frame.titlePanel.gameDate.SetLabel(gd.strftime("%a %b %d"))
        self.frame.titlePanel.gameTime.SetLabel(gd.strftime("%I:%M %p"))
        self.frame.titlePanel.hAbrv.SetLabel(info["teams"]["home"]["abrv"].upper())

        try:
            odds = info["odds"][-1]["99"]

            try:
                spread = odds["home_spread"] if float(odds["home_spread"]) < 0 else "+"+str(odds["home_spread"])
            except:
                spread = ""
            self.frame.titlePanel.spread.SetLabel("{}".format(spread))
            self.frame.titlePanel.ou.SetLabel("{}".format(odds["total"]))

        except:
            pass

        self.model.matchDB.openDB()
        for hA in ("away", "home"):
            team = info["teams"][hA]
            teamId = info["{}Id".format(hA)]
            name = "{} {}".format(team["firstName"], team["lastName"])

            try:
                logo = wx.Image(ENV.logoPath.format(self.model.leagueId, info["{}Id".format(hA)]), wx.BITMAP_TYPE_ANY).Scale(50, 50, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
            except:
                logo = wx.Image(ENV.logoPath.format(self.model.leagueId, -1), wx.BITMAP_TYPE_ANY).Scale(35, 35, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()


            self.frame.titlePanel.values[hA]["name"].SetLabel(name)
            self.frame.titlePanel.values[hA]["logo"].SetBitmap(logo)


            self.frame.titlePanel.values[hA]["hATag"].Hide()
            if self.model.options["hA"] =="Away/Home":
                self.frame.titlePanel.values[hA]["hATag"].Show()
                self.frame.titlePanel.values[hA]["hATag"].SetLabel(hA.upper())

            self.frame.titlePanel.values[hA]["tFTag"].SetLabel(self.model.options["tF"].upper())

            oD = "offense" if self.model.options["tO"] =="team" else "defense"
            self.frame.titlePanel.values[hA]["oDTag"].SetLabel(oD.upper())

            self.frame.titlePanel.values[hA]["wLTag"].Hide()
            if self.model.options["wL"] != "all":
                self.frame.titlePanel.values[hA]["wLTag"].Show()
                self.frame.titlePanel.values[hA]["wLTag"].SetLabel(self.model.options["wL"].upper())

            try:
                money = odds["{}_ml".format(hA)] if int(odds["{}_ml".format(hA)]) < 0 else "+"+str(odds["{}_ml".format(hA)])
            except:
                money = ''
            self.frame.titlePanel.values[hA]["moneyLine"].SetLabel(money)
        self.model.matchDB.closeDB()
        self.frame.titlePanel.Layout()


    def setGameLog(self):

        gameLogItems = ("gameDate", "hA", "oppId", "teamPts", "oppPts", "spread", "money", "ou", "spreadOutcome", "moneyOutcome", "ovOutcome")

        gdCmd = self.model.getGDCmd()

        for hA in ("away", "home"):

            teamId = self.model.getGame()["{}Id".format(hA)]
            andTS = self.model.getAndTSCmd(hA)
            andWL = self.model.getAndWLCmd(hA)
            andGL = self.model.getAndGLCmd(hA)
            andWGL = self.model.getAndWGLCmd(hA)
            whereGL = self.model.getWhereGLCmd(hA)

            oppTS = sub("team", "opp", andTS)
            oppWL = sub("team", "opp", andWL)

            if not search("-1", whereGL):
                # print(self._gameLogCmd.format({"gdCmd":gdCmd, "andTS": andTS, "andWL":andWL, "andWGL":andWGL, "andGL": andGL, "teamId": teamId, "oppTS": oppTS, "oppWL":oppWL, "whereGL": whereGL}))
                self.model.matchDB.openDB()
                games = self.model.matchDB.fetchAll(self._gameLogCmd.format({"gdCmd":gdCmd, "andTS": andTS, "andWL":andWL, "andWGL":andWGL, "andGL": andGL, "teamId": teamId, "oppTS": oppTS, "oppWL":oppWL, "whereGL": whereGL}))
                self.model.matchDB.closeDB()
                for game in games:
                    item = dict(zip(gameLogItems, game))
                    item["leagueId"] = self.model._leagueId
                    self.frame.panels['Game Log'].addGame(hA, item)
        self.frame.panels["Game Log"].Layout()


    def setGameLine(self):
        game = self.model.getGame()
        self.frame.panels["GameLine"].setPanel(game)
        self.frame.panels["GameLine"].Layout()


    @abstractmethod
    def setPlayerStats(self):
        pass


    def setGaming(self):
        gamingList = ("atsW", "atsL", "atsP", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$", "ou", "overLine", "underLine", "total", "over$", "under$")
        cmd = """
                SELECT IFNULL(SUM((CASE spread_outcome WHEN 1 THEN 1 ELSE 0 END)), 0) ats_wins,
                        IFNULL(SUM((CASE spread_outcome WHEN -1 THEN 1 ELSE 0 END)), 0) AS ats_loses,
                        IFNULL(SUM((CASE spread_outcome WHEN 0 THEN 1 ELSE 0 END)),0) AS ats_push,
                        AVG(spread), AVG(result), AVG(line), AVG(money),
                        SUM((CASE WHEN spread_outcome == 1 AND line > 0 THEN 100+line
                                WHEN spread_outcome == 1 AND line < 0 THEN (10000/(line*-1.0))+100
                                WHEN spread_outcome == 0 THEN 100
                                ELSE 0 END)),
                        SUM((CASE WHEN money_outcome == 1 AND money > 0 THEN 100+money
                                WHEN money_outcome == 1 AND money < 0 THEN (10000/(money*-1.0))+100
                                ELSE 0 END)),
                        AVG(ou), AVG(over_line), AVG(under_line), AVG(total),
                        SUM((CASE WHEN outcome == 1 AND line > 0 THEN 100+over_line
                                WHEN outcome == 1 AND line < 0 THEN (10000/(over_line*-1.0))+100
                                WHEN outcome == 0 THEN 100
                                ELSE 0 END)),
                        SUM((CASE WHEN outcome == -1 AND line > 0 THEN 100+under_line
                                WHEN outcome == -1 AND line < 0 THEN (10000/(under_line*-1.0))+100
                                WHEN outcome == 0 THEN 100
                                ELSE 0 END))
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN game_lines AS gl
                        ON gd.game_id = gl.game_id {0[andGL]} {0[andWGL]}
                    INNER JOIN over_unders AS ov
                        ON gl.game_id = ov.game_id
                    WHERE gl.{0[team]}_id = ? {0[whereGL]}
                """

        gdCmd = self.model.getGDCmd()
        for hA in ("away", "home"):
            panel = self.frame.panels['Gaming'].teams[hA]
            panel["name"].SetLabel("{} {} {}".format(("" if self.model.options["tO"] == "team" else "VS"),*[self.model.getGame()["teams"][hA][x] for x in ("firstName", "lastName")]))
            andGL = self.model.getAndGLCmd(hA)
            andWGL = self.model.getAndWGLCmd(hA)
            whereGL = sub("WHERE", "AND", self.model.getWhereGLCmd(hA))
            self.model.matchDB.openDB()
            gaming = dict(zip(gamingList, self.model.matchDB.fetchOne(cmd.format({"gdCmd":gdCmd, "andGL":andGL, "andWGL":andWGL, "whereGL":whereGL, "team":self.model.options["tO"]}), (self.model.getGame()["{}Id".format(hA)],))))
            self.model.matchDB.closeDB()

            totalBet = sum([gaming[t] for t in ("atsW","atsL", "atsP")])*100
            for key, value in gaming.items():
                try:
                    if key in ("money$", "ats$", "over$", "under$"):
                        result = ((value-totalBet)/totalBet)*100
                        panel[key].SetLabel("{:2.2f}%".format(result))
                    elif key in ("atsW", "atsL", "atsP"):
                        panel[key].SetLabel("{:2d}".format(value))
                    else:
                        panel[key].SetLabel("{:3.2f}".format(value))
                except (ZeroDivisionError, TypeError):
                    panel[key].SetLabel("--")
        self.frame.panels['Gaming'].Layout()


    def setInjuries(self):
        game = self.model.getGame()
        self.model.matchDB.openDB()
        for hA in ("away", "home"):
            injuries = []
            for playerId in game["players"][hA]:
                if playerId in game["injuries"].keys():
                    name = self.model.matchDB.fetchItem(self._injCmd, (playerId,))
                    injuries.append((name, *game["injuries"][playerId]))
            self.frame.panels["Injuries"].setPanel(hA, injuries)
        self.model.matchDB.closeDB()
        self.frame.panels["Injuries"].Layout()



    @abstractmethod
    def setTeamStats(self):
        pass
