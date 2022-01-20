import re

from .. import Environ as ENV
from ..Interfaces import Downloadable, Fileable
from ..Models import normal, yId

from pprint import pprint

################################################################################
################################################################################






################################################################################
################################################################################


class Player(Downloadable, Fileable):

    _info = None


    def __init__(self, *args, **kwargs):
        Downloadable.__init__(self, *args, **kwargs)
        Fileable.__init__(self, self._info, *args, **kwargs)

        self.playerId = None

        # pprint(self.info)


    def create(self, playerId):
        print("New {} Player {}".format(self.info["leagueId"], playerId))
        self.playerId = playerId
        self.setUrl()
        self.setFilePath()

        try:
            self.read()
        except FileNotFoundError:
            self.parseData()
            self.write()
        pprint(self.info)

    def setFilePath(self):
        self.filePath = ENV.playerFilePath.format(self.info, self.playerId)



    def setUrl(self):
        self.url = ENV.playerUrl.format(self.info, self.playerId)


    def parseData(self):
        stores = self.downloadItem()
        entityId = stores["PageStore"]["pageData"]["entityId"]
        player = stores["PlayersStore"]["players"][entityId]

        player["draft_team"].pop("team")
        pprint(player)
        raise

################################################################################
################################################################################


class NBAPlayer(Player):

    _info = {
                "leagueId": "nba",
                "slugId": "nba",
                "player_id": -1,
                "first_name": "N/A",
                "last_name": "N/A",
                "bio": {},
                "draft": {},
                "pos_id": -1,
                "headshot": None
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def parseData(self):
        stores = self.downloadItem()
        entityId = stores["PageStore"]["pageData"]["entityId"]
        player = stores["PlayersStore"]["players"][entityId]
        try:
            player["draft_team"].pop("team")
            player["draft_team"]["team_id"] = yId(player["draft_team"]["team_id"])
        except:
            player["draft_team"] = {}

        self.info["player_id"] = yId(player["player_id"])
        self.info["first_name"] = normal(player["first_name"])
        self.info["last_name"] = normal(player["last_name"])
        self.info["bio"] = player["bio"]
        self.info["draft"] = player["draft_team"]
        self.info["pos_id"] = yId(player["primary_position_id"])
        try:
            self.info["headshot"] = re.search("https://s.yimg.com/xe/i/us/sp/v/nba_cutout/players_l/\d*/\d*.png", player["image"]).group(0)
        except AttributeError:
            pass

        pprint(self.info)

################################################################################
################################################################################


class MLBPlayer(Player):

    _info = {
                "leagueId": "mlb",
                "slugId": "mlb",
                "player_id": -1,
                "first_name": "N/A",
                "last_name": "N/A",
                "bio": {},
                "draft": {},
                "bat": "N/A",
                "throw": "N/A",
                "pos_id": -1,
                "headshot": None
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def parseData(self):
        stores = self.downloadItem()
        entityId = stores["PageStore"]["pageData"]["entityId"]
        player = stores["PlayersStore"]["players"][entityId]
        try:
            player["draft_team"].pop("team")
            player["draft_team"]["team_id"] = yId(player["draft_team"]["team_id"])
        except KeyError:
            player["draft_team"] = {}

        self.info["player_id"] = yId(player["player_id"])
        self.info["first_name"] = normal(player["first_name"])
        self.info["last_name"] = normal(player["last_name"])
        self.info["bio"] = player["bio"]
        self.info["draft"] = player["draft_team"]
        self.info["bat"] = player["bat"]
        self.info["throw"] = player["throw"]
        self.info["pos_id"] = yId(player["primary_position_id"])
        try:
            self.info["headshot"] = re.search("https://s.yimg.com/xe/i/us/sp/v/mlb_cutout/players_l/\d*/\d*.png", player["image"]).group(0)
        except:
            pass


################################################################################
################################################################################


class NFLPlayer(Player):

    _info = {
                "leagueId": "nfl",
                "slugId": "nfl",
                "player_id": -1,
                "first_name": "N/A",
                "last_name": "N/A",
                "bio": {},
                "draft": {},
                "pos_id": -1,
                "headshot": None
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def parseData(self):
        stores = self.downloadItem()
        entityId = stores["PageStore"]["pageData"]["entityId"]
        player = stores["PlayersStore"]["players"][entityId]
        try:
            player["draft_team"].pop("team")
            player["draft_team"]["team_id"] = yId(player["draft_team"]["team_id"])
        except KeyError:
            player["draft_team"] = {}

        self.info["player_id"] = yId(player["player_id"])
        self.info["first_name"] = normal(player["first_name"])
        self.info["last_name"] = normal(player["last_name"])
        self.info["bio"] = player["bio"]
        self.info["draft"] = player["draft_team"]
        self.info["pos_id"] = yId(player["primary_position_id"])
        try:
            self.info["headshot"] = re.search("https://s.yimg.com/xe/i/us/sp/v/nfl_cutout/players_l/\d*/\d*.png", player["image"]).group(0)
        except:
            pass

################################################################################
################################################################################


class NCAAFPlayer(Player):

    _info = {
                "leagueId": "ncaaf",
                "slugId": "ncaaf",
                "player_id": -1,
                "first_name": "N/A",
                "last_name": "N/A",
                "bio": {},
                "pos_id": -1,
                "team_id": -1,
                "uni_num": -1
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def parseData(self):
        stores = self.downloadItem()
        entityId = stores["PageStore"]["pageData"]["entityId"]
        player = stores["PlayersStore"]["players"][entityId]

        self.info["player_id"] = yId(player["player_id"])
        self.info["first_name"] = normal(player["first_name"])
        self.info["last_name"] = normal(player["last_name"])
        self.info["bio"] = player["bio"]
        self.info["pos_id"] = yId(player["primary_position_id"])
        self.info["team_id"] = yId(player["team_id"])
        self.info["uni_num"] = player["uniform_number"]


################################################################################
################################################################################


class NCAABPlayer(Player):

    _info = {
                "leagueId": "ncaab",
                "slugId": "ncaab",
                "player_id": -1,
                "first_name": "N/A",
                "last_name": "N/A",
                "bio": {},
                "pos_id": -1,
                "team_id": -1,
                "uni_num": -1
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def parseData(self):
        stores = self.downloadItem()
        entityId = stores["PageStore"]["pageData"]["entityId"]
        player = stores["PlayersStore"]["players"][entityId]

        self.info["player_id"] = yId(player["player_id"])
        self.info["first_name"] = normal(player["first_name"])
        self.info["last_name"] = normal(player["last_name"])
        self.info["bio"] = player["bio"]
        self.info["pos_id"] = yId(player["primary_position_id"])
        self.info["team_id"] = yId(player["team_id"])
        self.info["uni_num"] = player["uniform_number"]
