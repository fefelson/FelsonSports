import os

from .Database import Database as DB, Table as TB


### Games Table
gamesTable = TB("games")
    ### Primary Key
gamesTable.addPk("game_id", "INT")
    ## Foreign Keys
gamesTable.addFk("home_id", "pro_teams", "team_id")
gamesTable.addFk("away_id", "pro_teams", "team_id")
gamesTable.addFk("winner_id", "pro_teams", "team_id")
gamesTable.addFk("loser_id", "pro_teams", "team_id")
    ## Table Cols
gamesTable.addCol("season", "INT")
gamesTable.addCol("year", "INT")
gamesTable.addCol("game_date", "REAL")
gamesTable.addCol("game_type", "TEXT")
gamesTable.addCol("game_time", "TEXT")
    ## Table Indexes
gamesTable.addIndex("season_date", "season, game_date")
###############



### ProPlayers Table
proPlayersTable = TB("pro_players")
    ### Primary Key
proPlayersTable.addPk("player_id", "INT")
    ## Table Cols
proPlayersTable.addCol("first_name", "TEXT", True)
proPlayersTable.addCol("last_name", "TEXT", True)
proPlayersTable.addCol("height", "INT", True)
proPlayersTable.addCol("weight", "INT", True)
proPlayersTable.addCol("birth_year", "INT", True)
proPlayersTable.addCol("birth_day", "REAL", True)
proPlayersTable.addCol("rookie_year", "INT", True)
###############


### PlayerPositions Table
playersPositionsTable = TB("players_positions")
    ### Primary Key
playersPositionsTable.addPk("players_positions", "INT")
    ## Foreign Keys
playersPositionsTable.addFk("pos_id", "position_types", "pos_id")
playersPositionsTable.addFk("player_id", "pro_players", "player_id")
    ## Table Indexes
playersPositionsTable.addIndex("player_pos", "player_id")
playersPositionsTable.addIndex("pos_player", "pos_id")
###############



### ProTeams Table
proTeamsTable = TB("pro_teams")
    ### Primary Key
proTeamsTable.addPk("team_id", "INT")
    ## Table Cols
proTeamsTable.addCol("abrv", "TEXT")
proTeamsTable.addCol("first_name", "TEXT")
proTeamsTable.addCol("last_name", "TEXT")
proTeamsTable.addCol("conference", "TEXT")
proTeamsTable.addCol("division", "TEXT")
proTeamsTable.addCol("primary_color", "TEXT")
proTeamsTable.addCol("secondary_color", "TEXT")
###############


### PlayerGames Table
lineupsTable = TB("lineups")
    ### Primary Key
lineupsTable.addPk("lineup_id", "INT")
    ### Foreign Key
lineupsTable.addFk("game_id", "games", "game_id")
lineupsTable.addFk("player_id", "pro_players", "player_id")
lineupsTable.addFk("team_id", "pro_teams", "team_id")
lineupsTable.addFk("opp_id", "pro_teams", "team_id")
    ## Table Cols
lineupsTable.addCol("active", "INT")
lineupsTable.addCol("starter", "INT")



### PlayerStats Table
playerStatsTable = TB("player_stats")
    ### Primary Key
playerStatsTable.addPk("player_stat_id", "INT")
    ### Foreign Key
playerStatsTable.addFk("game_id", "games", "game_id")
playerStatsTable.addFk("player_id", "pro_players", "player_id")
playerStatsTable.addFk("team_id", "pro_teams", "team_id")
playerStatsTable.addFk("opp_id", "pro_teams", "team_id")
    ## Table Cols
playerStatsTable.addCol("fga", "INT")
playerStatsTable.addCol("fgm", "INT")
playerStatsTable.addCol("fta", "INT")
playerStatsTable.addCol("ftm", "INT")
playerStatsTable.addCol("tpa", "INT")
playerStatsTable.addCol("tpm", "INT")
playerStatsTable.addCol("pts", "INT")
playerStatsTable.addCol("oreb", "INT")
playerStatsTable.addCol("dreb", "INT")
playerStatsTable.addCol("reb", "INT")
playerStatsTable.addCol("ast", "INT")
playerStatsTable.addCol("stl", "INT")
playerStatsTable.addCol("blk", "INT")
playerStatsTable.addCol("trn", "INT")
playerStatsTable.addCol("fls", "INT")
playerStatsTable.addCol("tfl", "INT")
playerStatsTable.addCol("ejs", "INT")
playerStatsTable.addCol("ff", "INT")
playerStatsTable.addCol("mins", "REAL")
playerStatsTable.addCol("plmin", "INT")
playerStatsTable.addCol("ba", "INT")
    ## Table Indexes
playerStatsTable.addIndex("player_game_stats", "player_id, game_id")
###############


### PlayerShots Table
playerShotsTable = TB("player_shots")
    ### Primary Key
playerShotsTable.addPk("player_shot_id", "INT")
    ### Foreign Key
playerShotsTable.addFk("game_id", "games", "game_id")
playerShotsTable.addFk("player_id", "pro_players", "player_id")
playerShotsTable.addFk("team_id", "pro_teams", "team_id")
playerShotsTable.addFk("opp_id", "pro_teams", "team_id")
playerShotsTable.addFk("assist_id", "pro_players", "player_id")
playerShotsTable.addFk("block_id", "pro_players", "player_id")
    ## Table Cols
playerShotsTable.addCol("pts", "INT")
playerShotsTable.addCol("made", "INT")
playerShotsTable.addCol("base_pct", "REAL")
playerShotsTable.addCol("side_pct", "REAL")
playerShotsTable.addCol("box", "INT")
playerShotsTable.addCol("distance", "INT")
playerShotsTable.addCol("fastbreak", "INT")
    ## Table Indexes
playerShotsTable.addIndex("player_shots", "game_id, player_id")
playerShotsTable.addIndex("shots_against", "game_id, team_id")
###############




### TeamStats Table
teamStatsTable = TB("team_stats")
    ### Primary Key
teamStatsTable.addPk("team_stat_id", "INT")
    ### Foreign Key
teamStatsTable.addFk("game_id", "games", "game_id")
teamStatsTable.addFk("team_id", "pro_teams", "team_id")
teamStatsTable.addFk("opp_id", "pro_teams", "team_id")
    ## Table Cols
teamStatsTable.addCol("b2b", "INT")
teamStatsTable.addCol("fga", "INT")
teamStatsTable.addCol("fgm", "INT")
teamStatsTable.addCol("fta", "INT")
teamStatsTable.addCol("ftm", "INT")
teamStatsTable.addCol("tpa", "INT")
teamStatsTable.addCol("tpm", "INT")
teamStatsTable.addCol("pts", "INT")
teamStatsTable.addCol("oreb", "INT")
teamStatsTable.addCol("dreb", "INT")
teamStatsTable.addCol("reb", "INT")
teamStatsTable.addCol("ast", "INT")
teamStatsTable.addCol("stl", "INT")
teamStatsTable.addCol("blk", "INT")
teamStatsTable.addCol("trn", "INT")
teamStatsTable.addCol("fls", "INT")
teamStatsTable.addCol("treb", "INT")
    ## Table Indexes
teamStatsTable.addIndex("team_game_stats", "team_id, game_id")
teamStatsTable.addIndex("opp_game_stats", "opp_id, game_id")
###############


### Positions Type Table
positionsTypeTable = TB("position_types")
    ### Primary Key
positionsTypeTable.addPk("pos_id", "INT")
    ## Table Cols
positionsTypeTable.addCol("title", "TEXT")
positionsTypeTable.addCol("abrv", "TEXT")
###############


### Game Lines Table
gameLinesTable = TB("game_lines")
    ### Primary Key
gameLinesTable.addPk("gl_id", "INT")
    ### Foreign Key
gameLinesTable.addFk("game_id", "games", "game_id")
gameLinesTable.addFk("team_id", "pro_teams", "team_id")
    ## Table Cols
gameLinesTable.addCol("spread", "REAL")
gameLinesTable.addCol("line", "INT")
gameLinesTable.addCol("money", "INT")
gameLinesTable.addCol("result", "INT")
gameLinesTable.addCol("spread_outcome", "INT")
gameLinesTable.addCol("money_outcome", "INT")

    ## Table Indexes
gameLinesTable.addIndex("lines_teams", "team_id, game_id")
###############


### Over Under Table
overUndersTable = TB("over_unders")
    ### Primary Key
overUndersTable.addPk("ou_id", "INT")
    ### Foreign Key
overUndersTable.addFk("game_id", "games", "game_id")
    ## Table Cols
overUndersTable.addCol("ou", "REAL")
overUndersTable.addCol("over_line", "REAL")
overUndersTable.addCol("under_line", "REAL")
overUndersTable.addCol("total", "INT")
overUndersTable.addCol("outcome", "INT")
    ## Table Indexes
overUndersTable.addIndex("ou_games", "game_id")
###############


### dkYahoo Table
dkYahooTable = TB("dk_yahoo")
    ### Table Cols
dkYahooTable.addCol("dk_id", "TEXT")
dkYahooTable.addCol("yahoo_id", "TEXT")
dkYahooTable.addCol("team_id", "TEXT")
    ### Primary Key
dkYahooTable.multiPk("yahoo_id, dk_id, team_id")
###############


### dkTeam Table
dkTeamTable = TB("dk_team")
    ### Primary Key
dkTeamTable.addPk("dk_id", "TEXT")
    ### Table Cols
dkTeamTable.addCol("team_id", "TEXT")
###############


### dkSheet Table
dkSheetTable = TB("dk_sheets")
    ### Primary Key
dkSheetTable.addPk("dk_sheet_id", "INT")
    ### Table Cols
dkSheetTable.addCol("game_type", "TEXT")
dkSheetTable.addCol("start_time", "REAL")
dkSheetTable.addCol("num_games", "INT")
dkSheetTable.addCol("game_date", "TEXT")
###############


### dkSheetGames Table
dkSheetGamesTable = TB("dk_sheet_games")
    ### Primary Key
dkSheetGamesTable.addPk("dk_sheet_game_id", "INT")
    ### Foreign Keys
dkSheetGamesTable.addFk("dk_sheet_id", "dk_sheets", "dk_sheet_id")
    ### Table Cols
dkSheetGamesTable.addCol("game_id", "INT")
###############


### dkPrice Table
dkPriceTable = TB("dk_prices")
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


positions = [{"pos_id": -1, "abrv": "UNK", "title": "Unknown"},
             {"pos_id": 1, "abrv": "PG", "title": "Point Guard"},
             {"pos_id": 2, "abrv": "SG", "title": "Shooting Guard"},
             {"pos_id": 3, "abrv": "G", "title": "Guard"},
             {"pos_id": 4, "abrv": "GF", "title": "Guard-Forward"},
             {"pos_id": 5, "abrv": "SF", "title": "Small Forward"},
             {"pos_id": 6, "abrv": "PF", "title": "Power Forward"},
             {"pos_id": 7, "abrv": "F", "title": "Forward"},
             {"pos_id": 8, "abrv": "FC", "title": "Forward-Center"},
             {"pos_id": 9, "abrv": "C", "title": "Center"}]


statTypes = [{"stat_id": 104, "abrv": "FGA", "title": 'Field Goals Attempted'},
             {"stat_id": 105, "abrv": "FGM", "title": "Field Goals Made"},
             {"stat_id": 107, "abrv": "FTA", "title": "Free Throws Attempted"},
             {"stat_id": 108, "abrv": "FTM", "title": "Free Throws Made"},
             {"stat_id": 110, "abrv": "3PA", "title": "3-pt Shots Attempted"},
             {"stat_id": 111, "abrv": "3PM", "title": "3-pt Shots Made"},
             {"stat_id": 113, "abrv": "PTS", "title": 'Points Scored'},
             {"stat_id": 114, "abrv": "OREB", "title": "Offensive Rebounds"},
             {"stat_id": 115, "abrv": "DREB", "title": "Defensive Rebounds"},
             {"stat_id": 116, "abrv": "REB", "title": "Total Rebounds"},
             {"stat_id": 117, "abrv": "AST", "title": "Assists"},
             {"stat_id": 118, "abrv": "STL", "title": "Steals"},
             {"stat_id": 119, "abrv": "BLK", "title": 'Blocked Shots'},
             {"stat_id": 120, "abrv": "TURN", "title": "Turnovers"},
             {"stat_id": 122, "abrv": "FLS", "title": "Personal Fouls"},
             {"stat_id": 13, "abrv": "PTS", "title": 'Points Scored'},
             {"stat_id": 131, "abrv": "TREB", "title": "Team Rebounds"},
             {"stat_id": 11, "abrv": "3PM", "title": "3-pt Shots Made"},
             {"stat_id": 14, "abrv": "OREB", "title": "Offensive Rebounds"},
             {"stat_id": 15, "abrv": "DREB", "title": "Defensive Rebounds"},
             {"stat_id": 16, "abrv": "REB", "title": "Total Rebounds"},
             {"stat_id": 17, "abrv": "AST", "title": "Assists"},
             {"stat_id": 18, "abrv": "STL", "title": "Steals"},
             {"stat_id": 19, "abrv": "BLK", "title": 'Blocked Shots'},
             {"stat_id": 20, "abrv": "TURN", "title": "Turnovers"},
             {"stat_id": 22, "abrv": "FLS", "title": "Personal Fouls"},
             {"stat_id": 24, "abrv": "TF", "title": "Technical Fouls"},
             {"stat_id": 25, "abrv": "EJ", "title": "Ejections"},
             {"stat_id": 26, "abrv": "FF", "title": "Flagrant Fouls"},
             {"stat_id": 3, "abrv": "MINS", "title": 'Minutes Played'},
             {"stat_id": 32, "abrv": "pl/mn", "title": "Plus Minus"},
             {"stat_id": 33, "abrv": "BA", "title": "Blocks Against"},
             {"stat_id": 4, "abrv": "FGA", "title": 'Field Goals Attempted'},
             {"stat_id": 5, "abrv": "FGM", "title": "Field Goals Made"},
             {"stat_id": 7, "abrv": "FTA", "title": "Free Throws Attempted"},
             {"stat_id": 8, "abrv": "FTM", "title": "Free Throws Made"},
             {"stat_id": 10, "abrv": "3PA", "title": "3-pt Shots Attempted"}]


teams = [{"abrv": "MIN", "team_id": "16", "conference": "Western", "division": "Northwest", "primary_color": "0c2340", "secondary_color": "236192", "first_name": "Minnesota", "last_name": "Timberwolves", "league": "nba", "yahoo_id": "16", "espn_id": "16"},
         {"abrv": "WAS", "team_id": "27", "conference": "Eastern", "division": "Southeast", "primary_color": "002b5c", "secondary_color": "e31837", "first_name": "Washington", "last_name": "Wizards", "league": "nba", "yahoo_id": "27", "espn_id": "27"},
         {"abrv": "BKN", "team_id": "17", "conference": "Eastern", "division": "Atlantic", "primary_color": "000000", "secondary_color": "ffffff", "first_name": "Brooklyn", "last_name": "Nets", "league": "nba", "yahoo_id": "17", "espn_id": "17"},
         {"abrv": "TOR", "team_id": "28", "conference": "Eastern", "division": "Atlantic", "primary_color": "ce1141", "secondary_color": "000000", "first_name": "Toronto", "last_name": "Raptors", "league": "nba", "yahoo_id": "28", "espn_id": "28"},
         {"abrv": "NY", "team_id": "18", "conference": "Eastern", "division": "Atlantic", "primary_color": "006bb6", "secondary_color": "f58426", "first_name": "New York", "last_name": "Knicks", "league": "nba", "yahoo_id": "18", "espn_id": "18"},
         {"abrv": "MEM", "team_id": "29", "conference": "Western", "division": "Southwest", "primary_color": "5d76a9", "secondary_color": "12173f", "first_name": "Memphis", "last_name": "Grizzlies", "league": "nba", "yahoo_id": "29", "espn_id": "29"},
         {"abrv": "ORL", "team_id": "19", "conference": "Eastern", "division": "Southeast", "primary_color": "0077c0", "secondary_color": "c4ced4", "first_name": "Orlando", "last_name": "Magic", "league": "nba", "yahoo_id": "19", "espn_id": "19"},
         {"abrv": "ATL", "team_id": "1", "conference": "Eastern", "division": "Southeast", "primary_color": "e03a3e", "secondary_color": "c1d32f", "first_name": "Atlanta", "last_name": "Hawks", "league": "nba", "yahoo_id": "1", "espn_id": "1"},
         {"abrv": "BOS", "team_id": "2", "conference": "Eastern", "division": "Atlantic", "primary_color": "007a33", "secondary_color": "ba9653", "first_name": "Boston", "last_name": "Celtics", "league": "nba", "yahoo_id": "2", "espn_id": "2"},
         {"abrv": "NO", "team_id": "3", "conference": "Western", "division": "Southwest", "primary_color": "0c2340", "secondary_color": "c8102e", "first_name": "New Orleans", "last_name": "Pelicans", "league": "nba", "yahoo_id": "3", "espn_id": "3"},
         {"abrv": "CHA", "team_id": "30", "conference": "Eastern", "division": "Southeast", "primary_color": "1D1160", "secondary_color": "00788c", "first_name": "Charlotte", "last_name": "Hornets", "league": "nba", "yahoo_id": "30", "espn_id": "30"},
         {"abrv": "CHI", "team_id": "4", "conference": "Eastern", "division": "Central", "primary_color": "ce1141", "secondary_color": "000000", "first_name": "Chicago", "last_name": "Bulls", "league": "nba", "yahoo_id": "4", "espn_id": "4"},
         {"abrv": "PHI", "team_id": "20", "conference": "Eastern", "division": "Atlantic", "primary_color": "006bb6", "secondary_color": "ed174c", "first_name": "Philadelphia", "last_name": "76ers", "league": "nba", "yahoo_id": "20", "espn_id": "20"},
         {"abrv": "CLE", "team_id": "5", "conference": "Eastern", "division": "Central", "primary_color": "6f263d", "secondary_color": "041e42", "first_name": "Cleveland", "last_name": "Cavaliers", "league": "nba", "yahoo_id": "5", "espn_id": "5"},
         {"abrv": "HOU", "team_id": "10", "conference": "Western", "division": "Southwest", "primary_color": "ce1141", "secondary_color": "000000", "first_name": "Houston", "last_name": "Rockets", "league": "nba", "yahoo_id": "10", "espn_id": "10"},
         {"abrv": "PHO", "team_id": "21", "conference": "Western", "division": "Pacific", "primary_color": "1d1160", "secondary_color": "e56020", "first_name": "Phoenix", "last_name": "Suns", "league": "nba", "yahoo_id": "21", "espn_id": "21"},
         {"abrv": "DAL", "team_id": "6", "conference": "Western", "division": "Southwest", "primary_color": "00538c", "secondary_color": "002b5e", "first_name": "Dallas", "last_name": "Mavericks", "league": "nba", "yahoo_id": "6", "espn_id": "6"},
         {"abrv": "IND", "team_id": "11", "conference": "Eastern", "division": "Central", "primary_color": "002d62", "secondary_color": "fdbb30", "first_name": "Indiana", "last_name": "Pacers", "league": "nba", "yahoo_id": "11", "espn_id": "11"},
         {"abrv": "POR", "team_id": "22", "conference": "Western", "division": "Northwest", "primary_color": "e03a3e", "secondary_color": "000000", "first_name": "Portland", "last_name": "Trail Blazers", "league": "nba", "yahoo_id": "22", "espn_id": "22"},
         {"abrv": "DEN", "team_id": "7", "conference": "Western", "division": "Northwest", "primary_color": "0e2240", "secondary_color": "fec524", "first_name": "Denver", "last_name": "Nuggets", "league": "nba", "yahoo_id": "7", "espn_id": "7"},
         {"abrv": "LAC", "team_id": "12", "conference": "Western", "division": "Pacific", "primary_color": "c8102e", "secondary_color": "1d42ba", "first_name": "Los Angeles", "last_name": "Clippers", "league": "nba", "yahoo_id": "12", "espn_id": "12"},
         {"abrv": "SAC", "team_id": "23", "conference": "Western", "division": "Pacific", "primary_color": "5a2d81", "secondary_color": "63727a", "first_name": "Sacramento", "last_name": "Kings", "league": "nba", "yahoo_id": "23", "espn_id": "23"},
         {"abrv": "DET", "team_id": "8", "conference": "Eastern", "division": "Central", "primary_color": "c8102e", "secondary_color": "006bb6", "first_name": "Detroit", "last_name": "Pistons", "league": "nba", "yahoo_id": "8", "espn_id": "8"},
         {"abrv": "LAL", "team_id": "13", "conference": "Western", "division": "Pacific", "primary_color": "552583", "secondary_color": "fdb927", "first_name": "Los Angeles", "last_name": "Lakers", "league": "nba", "yahoo_id": "13", "espn_id": "13"},
         {"abrv": "SA", "team_id": "24", "conference": "Western", "division": "Southwest", "primary_color": "c4ced4", "secondary_color": "000000", "first_name": "San Antonio", "last_name": "Spurs", "league": "nba", "yahoo_id": "24", "espn_id": "24"},
         {"abrv": "GS", "team_id": "9", "conference": "Western", "division": "Pacific", "primary_color": "1d428a", "secondary_color": "FDB927", "first_name": "Golden State", "last_name": "Warriors", "league": "nba", "yahoo_id": "9", "espn_id": "9"},
         {"abrv": "MIA", "team_id": "14", "conference": "Eastern", "division": "Southeast", "primary_color": "98002e", "secondary_color": "f9a01b", "first_name": "Miami", "last_name": "Heat", "league": "nba", "yahoo_id": "14", "espn_id": "14"},
         {"abrv": "OKC", "team_id": "25", "conference": "Western", "division": "Northwest", "primary_color": "007ac1", "secondary_color": "ef3b24", "first_name": "Oklahoma City", "last_name": "Thunder", "league": "nba", "yahoo_id": "25", "espn_id": "25"},
         {"abrv": "MIL", "team_id": "15", "conference": "Eastern", "division": "Central", "primary_color": "00471b", "secondary_color": "eee1c6", "first_name": "Milwaukee", "last_name": "Bucks", "league": "nba", "yahoo_id": "15", "espn_id": "15"},
         {"abrv": "UTA", "team_id": "26", "conference": "Western", "division": "Northwest", "primary_color": "002b5c", "secondary_color": "00471b", "first_name": "Utah", "last_name": "Jazz", "league": "nba", "yahoo_id": "26", "espn_id": "26"}]



class NBADB(DB):

    dbPath = os.environ["HOME"]+"/Yahoo/nba/nba.db"

    def __init__(self):
        super().__init__(self.dbPath)


    def getTableList(self):
        return (gamesTable, proTeamsTable, proPlayersTable, gameLinesTable, overUndersTable, lineupsTable, playerStatsTable,
                teamStatsTable, positionsTypeTable, playerShotsTable, playersPositionsTable, dkYahooTable,
                dkTeamTable, dkSheetTable, dkSheetGamesTable, dkPriceTable)


    def seed(self):

        self.insert(proPlayersTable, values=(0,0,0,0,0,0,0,0))

        for position in positions:
            self.insert(positionsTypeTable, info=position)

        for team in teams:
            self.insert(proTeamsTable, info=team)

        self.commit()
