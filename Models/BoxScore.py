from .. import Environ as ENV
from ..Interfaces import Downloadable, Fileable

from pprint import pprint

################################################################################
################################################################################






################################################################################
################################################################################


class BoxScore(Downloadable, Fileable):

    _boxFilePath = None
    _info = {
                "pageData": None,
                "gameData": None,
                "teamData": None,
                "playerData": None,
                "statsData": None
            }


    def __init__(self, leagueId, *args, **kwargs):
        Downloadable.__init__(self, *args, **kwargs)
        Fileable.__init__(self, self._info, *args, **kwargs)

        self.leagueId = leagueId

        # pprint(self.info)


    def create(self, gameInfo):
        # pprint(game)
        self.setUrl(gameInfo["url"])
        self.setFilePath(gameInfo)
        try:
            self.read()
        except FileNotFoundError:
            print("new BoxScore", self.filePath)
            self.parseData()
            self.write()


    def setUrl(self, url):
        self.url = url


    def setFilePath(self, gameInfo):
        gameInfo["leagueId"] = self.leagueId
        self.filePath = self._boxFilePath.format(gameInfo)


    def parseData(self):
        stores = self.downloadItem()
        self.info = self._info
        pageData = stores["PageStore"]["pageData"]
        self.info["pageData"] = pageData

        game = stores["GamesStore"]["games"][pageData["entityId"]]
        game.pop("media_stream")
        self.info["gameData"] = game
        self.info["teamData"] = stores["TeamsStore"]
        try:
        	self.info["playerData"] = stores["PlayersStore"]
        except:
        	pass
        self.info["statsData"] = stores["StatsStore"]


################################################################################
################################################################################



class DailyBoxScore(BoxScore):

    _boxFilePath = ENV.dailyFilePath

    def __init__(self, leagueId, *args, **kwargs):
        super().__init__(leagueId, *args, **kwargs)



class WeeklyBoxScore(BoxScore):

    _boxFilePath = ENV.weeklyFilePath

    def __init__(self, leagueId, *args, **kwargs):
        super().__init__(leagueId, *args, **kwargs)





################################################################################
################################################################################
