import os
import sqlite3
import re
import datetime

from itertools import chain

from .Database import Database as DB
from .Database import Table as TB

# for debugging
from pprint import pprint

################################################################################
################################################################################

### Games Table
gamesTable = Table("games")
    ### Primary Key
gamesTable.addPk("game_id", "INT")
    ## Foreign Keys
gamesTable.addFk("home_id", "pro_teams", "team_id")
gamesTable.addFk("away_id", "pro_teams", "team_id")
gamesTable.addFk("winner_id", "pro_teams", "team_id", True)
gamesTable.addFk("loser_id", "pro_teams", "team_id", True)
gamesTable.addFk("stadium_id", "stadiums", "stadium_id")
    ## Table Cols
gamesTable.addCol("season", "INT")
gamesTable.addCol("week", "INT")
gamesTable.addCol("game_type", "TEXT")
gamesTable.addCol("game_time", "TEXT")
gamesTable.addCol("outcome", "TEXT")
    ## Table Indexes
gamesTable.addIndex("season_date", "season, week")
###############



### ProPlayers Table
proPlayersTable = Table("pro_players")
    ### Primary Key
proPlayersTable.addPk("player_id", "INT")
    ## Table Cols
proPlayersTable.addCol("first_name", "TEXT")
proPlayersTable.addCol("last_name", "TEXT")
proPlayersTable.addFk("pos_id", "positions", "pos_id")
###############



### ProTeams Table
proTeamsTable = Table("pro_teams")
    ### Primary Key
proTeamsTable.addPk("team_id", "INT")
    ## Table Cols
proTeamsTable.addCol("abrv", "TEXT")
proTeamsTable.addCol("city", "TEXT")
proTeamsTable.addCol("mascot", "TEXT")
proTeamsTable.addCol("conference", "TEXT")
proTeamsTable.addCol("division", "TEXT")
proTeamsTable.addCol("primary_color", "TEXT")
proTeamsTable.addCol("secondary_color", "TEXT")
###############


### PlayerStats Table
playerStatsTable = Table("player_stats")
    ### Primary Key
playerStatsTable.addPk("player_stat_id", "INT")
    ### Foreign Key
playerStatsTable.addFk("game_id", "games", "game_id")
playerStatsTable.addFk("player_id", "pro_players", "player_id")
playerStatsTable.addFk("team_id", "pro_teams", "team_id")
playerStatsTable.addFk("opp_id", "pro_teams", "team_id")
playerStatsTable.addFk("stat_id", "stat_types", "stat_id")
    ## Table Cols
playerStatsTable.addCol("value", "REAL")
    ## Table Indexes
playerStatsTable.addIndex("player_game_stats", "stat_id, player_id")
###############


### TeamStats Table
teamStatsTable = Table("team_stats")
    ### Primary Key
teamStatsTable.addPk("team_stat_id", "INT")
    ### Foreign Key
teamStatsTable.addFk("game_id", "games", "game_id")
teamStatsTable.addFk("team_id", "pro_teams", "team_id")
teamStatsTable.addFk("opp_id", "pro_teams", "team_id")
teamStatsTable.addFk("stat_id", "stat_types", "stat_id")
    ## Table Cols
teamStatsTable.addCol("value", "REAL")
    ## Table Indexes
teamStatsTable.addIndex("team_game_stats", "team_id, stat_id")
###############


### StatTypes Table
statTypesTable = Table("stat_types")
    ### Primary Key
statTypesTable.addPk("stat_id", "INT")
    ## Table Cols
statTypesTable.addCol("title", "TEXT")
statTypesTable.addCol("abrv", "TEXT")
###############


### Positions Table
positionsTable = Table("positions")
    ### Primary Key
positionsTable.addPk("pos_id", "INT")
    ## Table Cols
positionsTable.addCol("title", "TEXT")
positionsTable.addCol("abrv", "TEXT")
###############


### Stadiums Table
stadiumsTable = Table("stadiums")
    ### Primary Key
stadiumsTable.addPk("stadium_id", "INT")
    ## Table Cols
stadiumsTable.addCol("title", "TEXT")
###############


### dkYahoo Table
dkYahooTable = Table("dk_yahoo")
    ### Table Cols
dkYahooTable.addCol("dk_id", "TEXT")
dkYahooTable.addCol("yahoo_id", "INT")
dkYahooTable.addFk("team_id", "pro_teams", "dk_id")
    ### Primary Key
dkYahooTable.multiPk("yahoo_id, team_id, dk_id")
###############


### dkTeam Table
dkTeamTable = Table("dk_team")
    ### Primary Key
dkTeamTable.addPk("dk_id", "TEXT")
    ### Table Cols
dkTeamTable.addCol("team_id", "INT")
###############


### dkSheet Table
dkSheetTable = Table("dk_sheets")
    ### Primary Key
dkSheetTable.addPk("dk_sheet_id", "INT")
    ### Table Cols
dkSheetTable.addCol("game_type", "TEXT")
dkSheetTable.addCol("start_time", "REAL")
dkSheetTable.addCol("num_games", "INT")
dkSheetTable.addCol("game_date", "TEXT")
###############


### dkSheetGames Table
dkSheetGamesTable = Table("dk_sheet_games")
    ### Primary Key
dkSheetGamesTable.addPk("dk_sheet_game_id", "INT")
    ### Foreign Keys
dkSheetGamesTable.addFk("dk_sheet_id", "dk_sheets", "dk_sheet_id")
    ### Table Cols
dkSheetGamesTable.addCol("game_id", "INT")
###############


### dkPrice Table
dkPriceTable = Table("dk_prices")
    ### Primary Key
dkPriceTable.addPk("dk_price_id", "INT")
    ### Foreign Keys
dkPriceTable.addFk("dk_sheet_id", "dk_sheets", "dk_sheet_id")
    ### Table Cols
dkPriceTable.addCol("dk_id", "INT")
dkPriceTable.addCol("team_id", "TEXT")
dkPriceTable.addCol("game_id", "INT")
dkPriceTable.addCol("price", "INT")
dkPriceTable.addCol("pos", "TEXT")
###############


statTypes = [{"stat_id": "111", "abrv": "Sackd", "title": "Sackd"},
            {"stat_id": "112", "abrv": "QBYdsL", "title": "Sacked Yards Lost"},
            {"stat_id": "310", "abrv": "Tgt", "title": "Targets"},
            {"stat_id": "102", "abrv": "PaComp", "title": "Completions"},
            {"stat_id": "113", "abrv": "QBRat", "title": "QB Rating"},
            {"stat_id": "3", "abrv": "FL", "title": "Fumbles Lost"},
            {"stat_id": "410", "abrv": "FGLong", "title": "Long"},
            {"stat_id": "103", "abrv": "PaAtt", "title": "Attempts"},
            {"stat_id": "950", "abrv": "TO", "title": "Turnovers"},
            {"stat_id": "411", "abrv": "XPM", "title": "Extra Points Made"},
            {"stat_id": "202", "abrv": "RuAtt", "title": "Rushes"},
            {"stat_id": "951", "abrv": "PASSEFF", "title": "Comp-Att"},
            {"stat_id": "412", "abrv": "XPA", "title": "Extra Points Attempted"},
            {"stat_id": "302", "abrv": "Rec", "title": "Receptions"},
            {"stat_id": "203", "abrv": "RuYds", "title": "Rushing Yards"},
            {"stat_id": "105", "abrv": "PaYds", "title": "Passing Yards"},
            {"stat_id": "941", "abrv": "3DE", "title": "Third Down Efficiency"},
            {"stat_id": "710", "abrv": "PD", "title": "Passes Defended"},
            {"stat_id": "512", "abrv": "PuntRetLong", "title": "Punt Return Longest"},
            {"stat_id": "413", "abrv": "Pts", "title": "Kicking Points"},
            {"stat_id": "303", "abrv": "RecYds", "title": "Receiving Yards"},
            {"stat_id": "920", "abrv": "Rushes", "title": "Rushes"},
            {"stat_id": "931", "abrv": "FUMB", "title": "Fumbles"},
            {"stat_id": "502", "abrv": "KR", "title": "Kickoff Returns"},
            {"stat_id": "513", "abrv": "PRTDs", "title": "Punt Return Touchdowns"},
            {"stat_id": "921", "abrv": "RuYds", "title": "Net Yards Rushing"},
            {"stat_id": "932", "abrv": "FL", "title": "Fumbles Lost"},
            {"stat_id": "602", "abrv": "P", "title": "Punts"},
            {"stat_id": "503", "abrv": "KRYds", "title": "Kick Return Yards"},
            {"stat_id": "206", "abrv": "RuLong", "title": "Longest Run"},
            {"stat_id": "108", "abrv": "PaTDs", "title": "Passing Touchdowns"},
            {"stat_id": "933", "abrv": "Pen", "title": "Penalties"},
            {"stat_id": "702", "abrv": "Solo", "title": "Solo Tackles"},
            {"stat_id": "944", "abrv": "4DE", "title": "Fourth Down Efficiency"},
            {"stat_id": "306", "abrv": "RecLong", "title": "Longest"},
            {"stat_id": "207", "abrv": "RuTDs", "title": "Rushing Touchdowns"},
            {"stat_id": "109", "abrv": "PaInts", "title": "Passing Interceptions"},
            {"stat_id": "934", "abrv": "PenYDs", "title": "Penalty Yards"},
            {"stat_id": "703", "abrv": "Ast", "title": "Tackle Assists"},
            {"stat_id": "945", "abrv": "YdS", "title": "Total Yards"},
            {"stat_id": "935", "abrv": "Poss", "title": "Time of Possession"},
            {"stat_id": "704", "abrv": "Takl", "title": "Total Tackles"},
            {"stat_id": "946", "abrv": "Plays", "title": "Total Plays"},
            {"stat_id": "605", "abrv": "PIn20", "title": "Punts in 20"},
            {"stat_id": "506", "abrv": "KRLong", "title": "Kick Return Longest"},
            {"stat_id": "407", "abrv": "FGM", "title": "Total FG Made"},
            {"stat_id": "936", "abrv": "RuF", "title": "Rushes for First"},
            {"stat_id": "705", "abrv": "Sack", "title": "Sacks"},
            {"stat_id": "947", "abrv": "NETPYDS", "title": "Net Yards Passing"},
            {"stat_id": "507", "abrv": "KRTDs", "title": "Kick Return Touchdowns"},
            {"stat_id": "408", "abrv": "FGA", "title": "Total Field Goals Attempted"},
            {"stat_id": "309", "abrv": "RecTDs", "title": "Recieving Touchdowns"},
            {"stat_id": "926", "abrv": "PaInts", "title": "Interceptions Thrown"},
            {"stat_id": "937", "abrv": "PASSF", "title": "Passes for First"},
            {"stat_id": "948", "abrv": "AVGPYDS", "title": "Yards Per Pass"},
            {"stat_id": "607", "abrv": "PTB", "title": "Touchbacks"},
            {"stat_id": "508", "abrv": "PR", "title": "Punt Returns"},
            {"stat_id": "927", "abrv": "SACKS", "title": "Times Sacked"},
            {"stat_id": "938", "abrv": "PENF", "title": "Penalties for First"},
            {"stat_id": "707", "abrv": "Ints", "title": "Interceptions"},
            {"stat_id": "608", "abrv": "PLong", "title": "Longest"},
            {"stat_id": "509", "abrv": "PRYds", "title": "Punt Return Yards"},
            {"stat_id": "928", "abrv": "SACKYD", "title": "Yds Lost To Sacks"},
            {"stat_id": "708", "abrv": "IntYds", "title": "Yards"},
            {"stat_id": "929", "abrv": "P", "title": "Punts"},
            {"stat_id": "709", "abrv": "IntTDs", "title": "Interception Touchdowns"},
            {"stat_id": "919", "abrv": "Firsts", "title": "First Downs"},
            {"stat_id": "1000", "abrv": "Pts", "title": "Team Points"}]


positionTypes = [{"pos_id": "7", "abrv": "TE", "title": "Tight End"},
                {"pos_id": "8", "abrv": "QB", "title": "Quarterback"},
                {"pos_id": "9", "abrv": "RB", "title": "Running Back"},
                {"pos_id": "90", "abrv": "SPTM", "title": "Special Teams"},
                {"pos_id": "92", "abrv": "KR", "title": "Kick Returner"},
                {"pos_id": "94", "abrv": "PR", "title": "Punt Returner"},
                {"pos_id": "30", "abrv": "LB", "title": "Linebacker"},
                {"pos_id": "20", "abrv": "SS", "title": "Strong Safety"},
                {"pos_id": "31", "abrv": "DE", "title": "Defensive End"},
                {"pos_id": "97", "abrv": "HLD", "title": "Holder"},
                {"pos_id": "21", "abrv": "FS", "title": "Free Safety"},
                {"pos_id": "32", "abrv": "DT", "title": "Defensive Tackle"},
                {"pos_id": "98", "abrv": "KFG", "title": "Kicker (FG)"},
                {"pos_id": "11", "abrv": "LDE", "title": "Left Defensive End"},
                {"pos_id": "22", "abrv": "K", "title": "Kicker"},
                {"pos_id": "99", "abrv": "KKO", "title": "Kicker (KO)"},
                {"pos_id": "12", "abrv": "NT", "title": "Nose Tackle"},
                {"pos_id": "23", "abrv": "P", "title": "Punter"},
                {"pos_id": "13", "abrv": "RDE", "title": "Right Defensive End"},
                {"pos_id": "14", "abrv": "LOLB", "title": "Left Outside Linebacker"},
                {"pos_id": "25", "abrv": "RDT", "title": "Right Defensive Tackle"},
                {"pos_id": "36", "abrv": "S", "title": "Safety"},
                {"pos_id": "15", "abrv": "LILB", "title": "Left Inside Linebacker"},
                {"pos_id": "27", "abrv": "MLB", "title": "Middle Linebacker"},
                {"pos_id": "29", "abrv": "CB", "title": "Cornerback"},
                {"pos_id": "19", "abrv": "RCB", "title": "Right Cornerback"},
                {"pos_id": "1", "abrv": "WR", "title": "Wide Receiver"}]


################################################################################
################################################################################


class NFLDatabase(Database, UpdateMixIn):

    def __init__(self):
        UpdateMixIn.__init__(self)
        Database.__init__(self, ENV.getPath("database", fileName="nfl"))


    def getManagerKey(self):
        return "dbEntries"


    def update(self):
        self.loadManagerFile()
        if self.checkUpdate():
            checkDate = self.getItem().date()
            self.insertDates(checkDate)
            self.updateManagerFile()
            self.commit()


    def getTableList(self):
        return (gamesTable, proPlayersTable, proTeamsTable, stadiumsTable, statTypesTable,
                playerStatsTable, teamStatsTable, positionsTable)


    def enterFileItems(self, itemType, itemTable):
        itemPath = ENV.getPath(itemType).strip("None.json")
        for itemFile in [itemPath+fileName for fileName in os.listdir(itemPath) if os.path.isfile(itemPath+fileName)]:
            info = ENV.getJsonInfo(itemFile)
            self.insert(itemTable, info=info)


    def insertGame(self, gamePath):
        pass


    def seed(self):
        self.clearManagerFile()
        self.enterFileItems("player", proPlayersTable)
        self.enterFileItems("team", proTeamsTable)

        for info in statTypes:
            self.insert(statTypesTable, info=info)

        for info in positionTypes:
            self.insert(positionsTable, info=info)

        self.commit()



################################################################################
################################################################################


class NFLDFS(Database):

    def __init__(self):
        super().__init__(ENV.getPath("dfs"))


    def getTableList(self):
        return (dkYahooTable, dkTeamTable, dkPriceTable, dkSheetTable,
                dkSheetGamesTable)


    def seed(self):
        pass


################################################################################
################################################################################

if __name__ == "__main__":
    db = NFLDatabase()
    db.openDB()
    db.closeDB()
