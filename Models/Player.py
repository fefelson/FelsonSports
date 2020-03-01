from abc import ABCMeta, abstractmethod
from ..Utils import SQL

################################################################################
################################################################################






################################################################################
################################################################################


class Player(metaclass=ABCMeta):

    def __init__(self, model, playerId):

        self.model = model
        self.playerId = playerId

        self.info = {}

        self.positions = []

        self.stats = {}

        self.setInfo()
        self.setStats()


    def __str__(self):
        return " ".join((self.info["firstName"], self.info["lastName"]))


    def __repr__(self):
        return " ".join((self.info["firstName"], self.info["lastName"]))


    def getId(self):
        return self.playerId


    def getInfo(self, label):
        return self.info[label]


    def setStats(self):
        timeFrame = self.model.getTimeFrame()
        db = self.model.getDB()
        gdCmd = self.model.gdDict[timeFrame]
        playerStats = dict(zip(("mins", "fga", "fgm", "fta", "ftm", "tpa", "tpm", "pts", "reb", "ast",
                                    "stl", "blk", "trn", "fls", "score"), db.fetchOne(SQL.playerAvgStats.format({"gdCmd":gdCmd, "scoreWhereCmd": "WHERE ps.player_id = ?"}), (self.playerId,))))
        self.stats[timeFrame] = playerStats


    def getStats(self, stat):
        timeFrame = self.model.getTimeFrame()
        try:
            playerStats = self.stats[timeFrame]
        except KeyError:
            self.setStats()
            playerStats = self.stats[timeFrame]
        return playerStats[stat]







################################################################################
################################################################################


class NBAPlayer(Player):

    def __init__(self, model, playerId):
        super().__init__(model, playerId)


    def setInfo(self):
        db = self.model.getDB()
        self.info["firstName"], self.info["lastName"] = db.fetchOne("SELECT first_name, last_name FROM pro_players WHERE player_id = ?", (self.playerId,))
        self.info["pos"] = [x[0] for x in db.fetchAll("SELECT pt.abrv FROM players_positions AS pp INNER JOIN position_types AS pt ON pp.pos_id = pt.pos_id WHERE player_id = ?", (self.playerId,))]



################################################################################
################################################################################


class NCAABPlayer(Player):

    def __init__(self, model, playerId):
        super().__init__(model, playerId)


    def setInfo(self):
        db = self.model.getDB()
        try:
            self.info["firstName"], self.info["lastName"], self.info["pos"] = db.fetchOne("SELECT first_name, last_name, abrv FROM col_players AS cp INNER JOIN position_types AS pt ON cp.pos_id = pt.pos_id WHERE player_id = ?", (self.playerId,))
        except:
            self.info["firstName"] = "N/A"
            self.info["lastName"] = "N/A"
            self.info["pos"] = "N/A"
