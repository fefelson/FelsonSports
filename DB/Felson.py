from .. import Environ as ENV
from .Database import Database as DB
from .Database import Table as TB
from .Data import *
from itertools import chain

# for debugging
# from pprint import pprint

################################################################################
################################################################################

### Leagues Table
leaguesTable = TB("leagues")
    ### Primary Key
leaguesTable.addPk("abrv", "TEXT")
    ## Table Cols
leaguesTable.addCol("name", "TEXT")
leaguesTable.addCol("espn_slug", "TEXT")
leaguesTable.addCol("yahoo_slug", "TEXT")
leaguesTable.addCol("espn_id", "TEXT")
leaguesTable.addCol("yahoo_id", "TEXT")
leaguesTable.addCol("current_season", "TEXT")
leaguesTable.addCol("start_date", "REAL")
leaguesTable.addCol("end_date", "REAL")
leaguesTable.addCol("season_phase", "INT")
leaguesTable.addCol("next_update", "REAL")
leaguesTable.addCol("is_active", "INT")
###############


### Seasons Table
seasonsTable = TB("seasons")
    ### Primary Key
seasonsTable.addPk("season_id", "INT")
    ## Foreign Keys
seasonsTable.addFk("league", "leagues", "abrv")
    ## Table Cols
seasonsTable.addCol("abrv", "TEXT")
seasonsTable.addCol("start_date", "TEXT")
seasonsTable.addCol("end_date", "TEXT")
seasonsTable.addCol("all_star", "TEXT")


### games Table
gamesTable = TB("games")
    ### Primary Key
gamesTable.addPk("game_id", "TEXT")
    ## Foreign Keys
gamesTable.addFk("league", "leagues", "abrv")
gamesTable.addFk("season", "seasons", "season_id")
gamesTable.addFk("home_id", "teams", "team_id")
gamesTable.addFk("away_id", "teams", "team_id")
    ## Table Cols
gamesTable.addCol("status", "TEXT")
gamesTable.addCol("year", "INT")
gamesTable.addCol("month", "INT")
gamesTable.addCol("day", "INT")
gamesTable.addCol("game_time", "TEXT")
gamesTable.addCol("home_score", "INT", True)
gamesTable.addCol("away_score", "INT", True)
gamesTable.addCol("espn_id", "TEXT", True)
gamesTable.addCol("yahoo_id", "TEXT", True)
    ## Table Indexes
gamesTable.addIndex("game_date", "year, month, day")
###############


### teams Table
teamsTable = TB("teams")
    ### Primary Key
teamsTable.addPk("team_id", "TEXT")
    ### Foreign Key
teamsTable.addFk("league", "leagues", "abrv")
    ## Table Cols
teamsTable.addCol("abrv", "TEXT")
teamsTable.addCol("first_name", "TEXT")
teamsTable.addCol("last_name", "TEXT")
teamsTable.addCol("conference", "TEXT", True)
teamsTable.addCol("division", "TEXT", True)
teamsTable.addCol("primary_color", "TEXT", True)
teamsTable.addCol("secondary_color", "TEXT", True)
teamsTable.addCol("espn_id", "TEXT", True)
teamsTable.addCol("yahoo_id", "TEXT", True)
###############


### Odds Table
oddsTable = TB("odds")
    ### Primary Key
oddsTable.addPk("odds_id", "INT")
    ### Foreign Key
oddsTable.addFk("game_id", "games", "game_id")
    ## Table Cols
oddsTable.addCol("timestamp", "REAL")
oddsTable.addCol("home_line", "REAL", True)
oddsTable.addCol("away_line", "REAL", True)
oddsTable.addCol("home_money", "REAL", True)
oddsTable.addCol("away_money", "REAL", True)
oddsTable.addCol("home_total", "REAL", True)
oddsTable.addCol("away_total", "REAL", True)
oddsTable.addCol("over_under", "REAL", True)
    ## Table Indexes
oddsTable.addIndex("odds_games", "game_id")
###############


felsonLeagues = (   # abrv, name, espn_slug, yahoo_slug, espn_id, yahoo_id
                    ("nfl", "National Football League", "nfl", "nfl", 28, "nfl"),
                    ("nba", "National Basketball Association", "nba", "nba", 46, "nba"),
                    ),
                    ("ncaab", "NCAA College Basketball", "mens-college-basketball", "college-basketball", 41, "ncaab"),
                    ("ncaaf", "NCAA College Football", "college-football", "college-football", 23, "ncaaf")
                )


################################################################################
################################################################################


class FelsonDatabase(DB):

    dbPath = ENV.mainPath+"/felson.db"

    def __init__(self):
        super().__init__(self.dbPath)


    def getTableList(self):
        return (leaguesTable, seasonsTable, gamesTable, teamsTable, oddsTable)


    def seed(self):

        for league in felsonLeagues:
            self.insert(leaguesTable, values=(*league, ))

        for team in chain(MLBteams, NBAteams, NFLteams):
            self.insert(teamsTable, info=team)

        for season in chain()

        self.commit()



################################################################################
################################################################################
