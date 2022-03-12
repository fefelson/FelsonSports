from ..Sports import NBA, MLB, NCAAB, NFL, NCAAF


class FelsonModel:

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
