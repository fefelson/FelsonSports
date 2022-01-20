from copy import deepcopy
from datetime import date, datetime, timedelta

from .. import Environ as ENV
from ..Interfaces import Downloadable, Fileable, Updatable
from ..Models import yId


from pprint import pprint

################################################################################
################################################################################

playerCmd = """
            SELECT player_id, first_name, last_name
                FROM players
                WHERE player_id = ?
            """



################################################################################
################################################################################


class Matchup(Downloadable, Fileable, Updatable):

    _info =  {
                "gameId": -1,
                "gameTime": None,
                "leagueId": None,
                "homeId": -1,
                "awayId": -1,
                "url": None,
                "season": -1,
                "week": -1,
                "month": -1,
                "day": -1,
                "seasonPhase": -1,
                "players": {"away":{}, "home":{}},
                "teams": {"away":{}, "home":{}},
                "odds":[],
                "injuries":{},
                "injData": False,
                "lastUpdate": None,
                }

    _matchFilePath = None


    def __init__(self, league, *args, **kwargs):
        Downloadable.__init__(self, *args, **kwargs)
        Fileable.__init__(self, self._info, *args, **kwargs)
        Updatable.__init__(self, *args, **kwargs)

        self.league = league



    def create(self, gameInfo):
        self.info = deepcopy(self._info)
        self.info["season"] = self.league._info["currentSeason"]
        self.parseData(gameInfo)
        self.toWrite = False

        self.setUrl(gameInfo["url"])
        self.setFilePath(gameInfo)

        try:
            self.read()
        except FileNotFoundError:
            print("new Matchup", self.filePath)
            self.teamData()
            data = self.downloadItem()
            self.playerData(data)
            self.injuryData(data)
            self.toWrite = True


        if self.checkInjData():
            data = self.downloadItem()
            self.injuryData(data)
            self.info["injData"] = True
            self.toWrite = True


        self.checkWrite()
        if self.toWrite:
            print("writing")
            self.info["odds"].append(gameInfo["odds"][0])
            self.update()


    def checkInjData(self):

        inj = False
        now = datetime.now()

        print(now, datetime.strptime(self.info["gameTime"], "%a, %d %b %Y %H:%M:%S %z"))

        checkTime = (datetime.strptime(self.info["gameTime"], "%a, %d %b %Y %H:%M:%S %z")- timedelta(hours=4))
        if now.timestamp() > checkTime.timestamp() and not self.info["injData"]:
            inj = True

        return inj


    def determineUpdates(self):
        pass


    def parseData(self, game):
        for key in self.info.keys():
            if key not in ("odds", "players", "injuries", "lastUpdate", "season"):
                try:
                    self.info[key] = deepcopy(game[key])
                # TODO: change this for dict integrity
                except KeyError:
                    pass


    def playerData(self, stores):

        pageData = stores["PageStore"]["pageData"]
        game = stores["GamesStore"]["games"][pageData["entityId"]]


        for hA in ("home", "away"):
            label = "{}Id".format(hA)
            try:
                players = [yId(p) for p in game["playersByTeam"]["{}.t.{}".format(self.info["leagueId"], self.info[label])]]
                if players != self.info["players"][hA]:
                    self.info["players"][hA] = players
                    setData = True
            except KeyError:
                pass


    def injuryData(self, stores):

        pageData = stores["PageStore"]["pageData"]
        game = stores["GamesStore"]["games"][pageData["entityId"]]

        try:
            injury = [player["injury"] for player in stores["PlayersStore"]["players"].values() if player.get("injury", None)]
            self.info["injuries"] = {}
            for player in injury:
                playerId = yId(player["player_id"])
                self.info["injuries"][playerId] = (player["comment"], player["date"], player["type"])
        except KeyError:
            pass



    def setUrl(self, url):
        self.url = url


    def teamData(self):
        cmd = "SELECT team_id, abrv, first_name, last_name FROM teams WHERE team_id = ?"

        for hA in ("away", "home"):
            self.info["teams"][hA] = dict(zip(("teamId", "abrv", "firstName", "lastName"), self.league.dbManager.fetchOne(cmd, (self.info["{}Id".format(hA)], ))))



    def update(self):
        self.info["lastUpdate"] = str(datetime.today())
        self.write()



    def setFilePath(self, gameInfo):
        self.filePath = self._matchFilePath.format(gameInfo)






################################################################################
################################################################################


class DailyMatchup(Matchup):

    _matchFilePath = ENV.dailyMatchPath
    _updateTime = 1

    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def checkUpdate(self):
        update = False
        lastUpdate = datetime.fromisoformat(self.info["lastUpdate"])
        # print(lastUpdate + timedelta(hours=self._updateTime), datetime.today(), lastUpdate + timedelta(hours=self._updateTime) < datetime.today())
        # raise
        if lastUpdate + timedelta(hours=self._updateTime) < datetime.today():
            update = True
        return update


    def checkWrite(self):
        if self.info["lastUpdate"]:
            lastUpdate = datetime.fromisoformat(self.info["lastUpdate"])
            # print(lastUpdate + timedelta(hours=self._updateTime), datetime.today(), lastUpdate + timedelta(hours=self._updateTime) < datetime.today())
            # raise
            if lastUpdate + timedelta(hours=self._updateTime) < datetime.today():
                self.toWrite = True
        else:
            self.toWrite = True

        return self.toWrite




class WeeklyMatchup(Matchup):

    _matchFilePath = ENV.weeklyMatchPath
    _updateWeekTime = 5
    _updateDayTime = 1

    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def checkUpdate(self):
        update = False
        lastUpdate = datetime.fromisoformat(self.info["lastUpdate"])
        today = datetime.now()
        gameTime = datetime.strptime(self.info["gameTime"], "%a, %d %b %Y %H:%M:%S %z")-timedelta(hours=4)
        if today.month == gameTime.month and today.day == gameTime.day:
            if lastUpdate + timedelta(hours=self._updateDayTime) < datetime.today():
                update = True
        else:
            if lastUpdate + timedelta(hours=self._updateWeekTime) < datetime.today():
                update = True

        return update


    def checkWrite(self):
        if self.info["lastUpdate"]:
            lastUpdate = datetime.fromisoformat(self.info["lastUpdate"])
            today = datetime.now()
            gameTime = datetime.strptime(self.info["gameTime"], "%a, %d %b %Y %H:%M:%S %z")-timedelta(hours=4)
            if today.month == gameTime.month and today.day == gameTime.day:
                if lastUpdate + timedelta(hours=self._updateDayTime) < datetime.today():
                    self.toWrite = True
            else:
                if lastUpdate + timedelta(hours=self._updateWeekTime) < datetime.today():
                    self.toWrite = True
        else:
            self.toWrite = True
