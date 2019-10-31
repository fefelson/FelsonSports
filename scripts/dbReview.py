import MLBProjections.MLBProjections.DB.MLB as DB
from pprint import pprint





class Model:

    def __init__(self):

        sheetId = 3
        self.fantasyDB = DB.MLBDFS()
        self.fantasyDB.openDB()

        self.gameDBs = {}

        self.gameIds = [x[0] for x in self.fantasyDB.fetchAll("SELECT game_id FROM dk_sheet_games WHERE dk_sheet_id = ?",(sheetId,))]
        self.gameDate = self.fantasyDB.fetchOne("SELECT game_date FROM dk_sheets WHERE dk_sheet_id = ?",(sheetId,))[0]


        self.players = {"P":[],
                        "C":[],
                        "1B":[],
                           "2B":[],
                           "3B":[],
                           "SS":[],
                           "OF":[]}

        for gameId in self.gameIds:
            gameDB = DB.MLBGame(gameId)
            gameDB.openDB()
            self.gameDBs[gameId] = gameDB

            starters = [x[0] for x in gameDB.fetchAll("SELECT player_id FROM bullpens WHERE starter = 1")]
            for starter in starters:
                name, price, avgGame = self.fantasyDB.fetchOne("SELECT dk_id, price, avg_game FROM dk_prices INNER JOIN dk_yahoo ON dk_prices.yahoo_id = dk_yahoo.yahoo_id WHERE dk_prices.yahoo_id = ? AND dk_sheet_id = ?",(starter,sheetId))

                total = gameDB.fetchOne("SELECT COUNT(pitcher_id)  FROM sim_pitcher_stats WHERE pitcher_id = ?",(starter,))[0]
                count = gameDB.fetchOne("SELECT COUNT(score) FROM (SELECT (outs *.75) + (k *2.0) + (er *-2.0) + (h *-.6) + (bb *-.6) AS score FROM sim_pitcher_stats WHERE pitcher_id = ? GROUP BY sim_game_id) WHERE score >=20",(starter,))[0]
    
                self.players["P"].append((starter, gameId, name, price, count/total))

            batters = [x[0] for x in gameDB.fetchAll("SELECT player_id FROM lineups")]
            for playerId in batters:
                try:
                    name, price, pos, avgGame = self.fantasyDB.fetchOne("SELECT dk_id, price, pos, avg_game FROM dk_prices INNER JOIN dk_yahoo ON dk_prices.yahoo_id = dk_yahoo.yahoo_id WHERE dk_prices.yahoo_id = ? AND dk_sheet_id = ?",(playerId,sheetId))
                    for p in pos.split(","):
                        if p != "P":
                            total = gameDB.fetchOne("SELECT COUNT(batter_id) FROM sim_batter_stats WHERE batter_id = ?",(playerId,))[0]
                            count = gameDB.fetchOne("SELECT SUM(hr) FROM FROM sim_batter_stats WHERE batter_id = ? GROUP BY sim_game_id",(playerId,))[0]
                            self.players[p].append((playerId, gameId, name, price, count))
                except TypeError:
                    pass
                            
        for key, value in self.players.items():
            self.players[key] = sorted(value, key=lambda x: x[-1],reverse= True)

    def __del__(self):
        self.fantasyDB.closeDB()
        for gameDB in self.gameDBs.values():
            gameDB.closeDB()


if __name__ == "__main__":
    model = Model()
    pprint(model.players)
