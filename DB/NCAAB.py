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
colPlayersTable = TB("col_players")
    ### Primary Key
colPlayersTable.addPk("player_id", "INT")
    ### Foreign Key
colPlayersTable.addFk("team_id", "col_teams", "team_id")
    ## Table Cols
colPlayersTable.addCol("first_name", "TEXT", True)
colPlayersTable.addCol("last_name", "TEXT", True)
colPlayersTable.addCol("number", "INT", True)
colPlayersTable.addFk("pos_id", "position_types", "pos_id")
###############



### ProTeams Table
colTeamsTable = TB("col_teams")
    ### Primary Key
colTeamsTable.addPk("team_id", "INT")
    ## Table Cols
colTeamsTable.addCol("abrv", "TEXT")
colTeamsTable.addCol("first_name", "TEXT")
colTeamsTable.addCol("last_name", "TEXT")
colTeamsTable.addCol("conference", "TEXT")
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
playerStatsTable.addCol("mins", "REAL")
    ## Table Indexes
playerStatsTable.addIndex("player_game_stats", "player_id, game_id")
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
             {"pos_id": 1, "abrv": "G", "title": "Guard"},
             {"pos_id": 2, "abrv": "F", "title": "Forward"},
             {"pos_id": 3, "abrv": "C", "title": "Center"}]


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


teams = [{'abrv': 'CSUB', 'team_id': '1105', 'conference': 'Western Athletic', 'first_name': 'Bakersfield', 'last_name': 'Roadrunners'}, {'abrv': 'APP', 'team_id': '16', 'conference': 'Sun Belt', 'first_name': 'Appalachian State', 'last_name': 'Mountaineers'}, {'abrv': 'VERM', 'team_id': '616', 'conference': 'America East', 'first_name': 'Vermont', 'last_name': 'Catamounts'}, {'abrv': 'SE LA', 'team_id': '506', 'conference': 'Southland', 'first_name': 'Southeastern Louisiana', 'last_name': 'Lions'}, {'abrv': 'WAG', 'team_id': '627', 'conference': 'Northeast', 'first_name': 'Wagner', 'last_name': 'Seahawks'}, {'abrv': 'SCST', 'team_id': '517', 'conference': 'Mid-Eastern', 'first_name': 'South Carolina State', 'last_name': 'Bulldogs'}, {'abrv': 'WIU', 'team_id': '638', 'conference': 'Summit', 'first_name': 'Western Illinois', 'last_name': 'Leathernecks'}, {'abrv': 'SIU', 'team_id': '528', 'conference': 'Missouri Valley', 'first_name': 'Southern Illinois', 'last_name': 'Salukis'}, {'abrv': 'WINTH', 'team_id': '649', 'conference': 'Big South', 'first_name': 'Winthrop', 'last_name': 'Eagles'}, {'abrv': 'UNI', 'team_id': '418', 'conference': 'Missouri Valley', 'first_name': 'UNI', 'last_name': 'Panthers'}, {'abrv': 'LSU', 'team_id': '319', 'conference': 'Southeastern', 'first_name': 'LSU', 'last_name': 'Tigers'}, {'abrv': 'CWPO', 'team_id': '1611', 'conference': 'New York Collegiate Athle', 'first_name': 'LIU Post', 'last_name': 'Pioneers'}, {'abrv': 'UVU', 'team_id': '1424', 'conference': 'Western Athletic', 'first_name': 'Utah Valley', 'last_name': 'Wolverines'}, {'abrv': 'ARIZ', 'team_id': '17', 'conference': 'Pac-12', 'first_name': 'Arizona', 'last_name': 'Wildcats'}, {'abrv': 'AUB', 'team_id': '28', 'conference': 'Southeastern', 'first_name': 'Auburn', 'last_name': 'Tigers'}, {'abrv': 'UCLA', 'team_id': '606', 'conference': 'Pac-12', 'first_name': 'UCLA', 'last_name': 'Bruins'}, {'abrv': 'NOVA', 'team_id': '617', 'conference': 'Big East', 'first_name': 'Villanova', 'last_name': 'Wildcats'}, {'abrv': 'SEA', 'team_id': '507', 'conference': 'Western Athletic', 'first_name': 'Seattle', 'last_name': 'Redhawks'}, {'abrv': 'WAKE', 'team_id': '628', 'conference': 'Atlantic Coast', 'first_name': 'Wake Forest', 'last_name': 'Demon Deacons'}, {'abrv': 'WKU', 'team_id': '639', 'conference': 'Conference USA', 'first_name': 'Western Kentucky', 'last_name': 'Hilltoppers'}, {'abrv': 'NIAG', 'team_id': '408', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Niagara', 'last_name': 'Purple Eagles'}, {'abrv': 'CSUN', 'team_id': '419', 'conference': 'Big West', 'first_name': 'CSUN', 'last_name': 'Matadors'}, {'abrv': 'LIU', 'team_id': '309', 'conference': 'Northeast', 'first_name': 'LIU', 'last_name': 'Sharks'}, {'abrv': 'N OMA', 'team_id': '1337', 'conference': 'Summit', 'first_name': 'Omaha', 'last_name': 'Mavericks'}, {'abrv': 'SDAK', 'team_id': '1458', 'conference': 'Summit', 'first_name': 'South Dakota', 'last_name': 'Coyotes'}, {'abrv': 'SHU', 'team_id': '1118', 'conference': 'Northeast', 'first_name': 'Sacred Heart', 'last_name': 'Pioneers'}, {'abrv': 'ASU', 'team_id': '18', 'conference': 'Pac-12', 'first_name': 'Arizona State', 'last_name': 'Sun Devils'}, {'abrv': 'UVA', 'team_id': '618', 'conference': 'Atlantic Coast', 'first_name': 'Virginia', 'last_name': 'Cavaliers'}, {'abrv': 'SHU', 'team_id': '508', 'conference': 'Big East', 'first_name': 'Seton Hall', 'last_name': 'Pirates'}, {'abrv': 'NICH', 'team_id': '409', 'conference': 'Southland', 'first_name': 'Nicholls', 'last_name': 'Colonels'}, {'abrv': 'CABAP', 'team_id': '1009', 'conference': 'Western Athletic', 'first_name': 'California Baptist', 'last_name': 'Lancers'}, {'abrv': 'ARK', 'team_id': '19', 'conference': 'Southeastern', 'first_name': 'Arkansas', 'last_name': 'Razorbacks'}, {'abrv': 'SEMO', 'team_id': '509', 'conference': 'Ohio Valley', 'first_name': 'Southeast Missouri State', 'last_name': 'Redhawks'}, {'abrv': 'USC', 'team_id': '609', 'conference': 'Pac-12', 'first_name': 'USC', 'last_name': 'Trojans'}, {'abrv': 'LONGW', 'team_id': '1219', 'conference': 'Big South', 'first_name': 'Longwood', 'last_name': 'Lancers'}, {'abrv': 'NCCU', 'team_id': '907', 'conference': 'Mid-Eastern', 'first_name': 'North Carolina Central', 'last_name': 'Eagles'}, {'abrv': 'N KY', 'team_id': '1506', 'conference': 'Horizon', 'first_name': 'Northern Kentucky', 'last_name': 'Norse'}, {'abrv': 'IW', 'team_id': '1528', 'conference': 'Southland', 'first_name': 'UIW', 'last_name': 'Cardinals'}, {'abrv': 'MERR', 'team_id': '1519', 'conference': 'Northeast', 'first_name': 'Merrimack', 'last_name': 'Warriors'}, {'abrv': 'EKY', 'team_id': '180', 'conference': 'Ohio Valley', 'first_name': 'Eastern Kentucky', 'last_name': 'Colonels'}, {'abrv': 'JKST', 'team_id': '280', 'conference': 'Southwestern Athletic', 'first_name': 'Jackson State', 'last_name': 'Tigers'}, {'abrv': 'DRKE', 'team_id': '170', 'conference': 'Missouri Valley', 'first_name': 'Drake', 'last_name': 'Bulldogs'}, {'abrv': 'KENT', 'team_id': '291', 'conference': 'Mid-American', 'first_name': 'Kent State', 'last_name': 'Golden Flashes'}, {'abrv': 'EMU', 'team_id': '181', 'conference': 'Mid-American', 'first_name': 'Eastern Michigan', 'last_name': 'Eagles'}, {'abrv': 'DSU', 'team_id': '160', 'conference': 'Mid-Eastern', 'first_name': 'Delaware State', 'last_name': 'Hornets'}, {'abrv': 'JXVL', 'team_id': '281', 'conference': 'Atlantic Sun', 'first_name': 'Jacksonville', 'last_name': 'Dolphins'}, {'abrv': 'UK', 'team_id': '292', 'conference': 'Southeastern', 'first_name': 'Kentucky', 'last_name': 'Wildcats'}, {'abrv': 'EVAN', 'team_id': '193', 'conference': 'Missouri Valley', 'first_name': 'Evansville', 'last_name': 'Aces'}, {'abrv': 'IUPUI', 'team_id': '1090', 'conference': 'Horizon', 'first_name': 'IUPUI', 'last_name': 'Jaguars'}, {'abrv': 'MONM', 'team_id': '370', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Monmouth', 'last_name': 'Hawks'}, {'abrv': 'MURR', 'team_id': '381', 'conference': 'Ohio Valley', 'first_name': 'Murray State', 'last_name': 'Racers'}, {'abrv': 'IND', 'team_id': '271', 'conference': 'Big Ten', 'first_name': 'Indiana', 'last_name': 'Hoosiers'}, {'abrv': 'NAVY', 'team_id': '392', 'conference': 'Patriot League', 'first_name': 'Navy', 'last_name': 'Midshipmen'}, {'abrv': 'JMU', 'team_id': '282', 'conference': 'Colonial', 'first_name': 'James Madison', 'last_name': 'Dukes'}, {'abrv': 'DREX', 'team_id': '172', 'conference': 'Colonial', 'first_name': 'Drexel', 'last_name': 'Dragons'}, {'abrv': 'TENN', 'team_id': '580', 'conference': 'Southeastern', 'first_name': 'Tennessee', 'last_name': 'Volunteers'}, {'abrv': 'PRE', 'team_id': '470', 'conference': 'Big South', 'first_name': 'Presbyterian', 'last_name': 'Blue Hose'}, {'abrv': 'TXSO', 'team_id': '591', 'conference': 'Southwestern Athletic', 'first_name': 'Texas Southern', 'last_name': 'Tigers'}, {'abrv': 'RUTG', 'team_id': '492', 'conference': 'Big Ten', 'first_name': 'Rutgers', 'last_name': 'Scarlet Knights'}, {'abrv': 'UNCA', 'team_id': '393', 'conference': 'Big South', 'first_name': 'UNC Asheville', 'last_name': 'Bulldogs'}, {'abrv': 'DUKE', 'team_id': '173', 'conference': 'Atlantic Coast', 'first_name': 'Duke', 'last_name': 'Blue Devils'}, {'abrv': 'EWU', 'team_id': '184', 'conference': 'Big Sky', 'first_name': 'Eastern Washington', 'last_name': 'Eagles'}, {'abrv': 'ELON', 'team_id': '195', 'conference': 'Colonial', 'first_name': 'Elon', 'last_name': 'Phoenix'}, {'abrv': 'PENN', 'team_id': '460', 'conference': 'Ivy League', 'first_name': 'Penn', 'last_name': 'Quakers'}, {'abrv': 'CHAT', 'team_id': '581', 'conference': 'Southern', 'first_name': 'Chattanooga', 'last_name': 'Mocs'}, {'abrv': 'MERC', 'team_id': '350', 'conference': 'Southern', 'first_name': 'Mercer', 'last_name': 'Bears'}, {'abrv': 'PRIN', 'team_id': '471', 'conference': 'Ivy League', 'first_name': 'Princeton', 'last_name': 'Tigers'}, {'abrv': 'TTU', 'team_id': '592', 'conference': 'Big 12', 'first_name': 'Texas Tech', 'last_name': 'Red Raiders'}, {'abrv': 'COPP', 'team_id': '130', 'conference': 'Mid-Eastern', 'first_name': 'Coppin State', 'last_name': 'Eagles'}, {'abrv': 'MONT', 'team_id': '372', 'conference': 'Big Sky', 'first_name': 'Montana', 'last_name': 'Grizzlies'}, {'abrv': 'DENV', 'team_id': '163', 'conference': 'Summit', 'first_name': 'Denver', 'last_name': 'Pioneers'}, {'abrv': 'JVST', 'team_id': '284', 'conference': 'Ohio Valley', 'first_name': 'Jacksonville State', 'last_name': 'Gamecocks'}, {'abrv': 'DUQ', 'team_id': '174', 'conference': 'Atlantic 10', 'first_name': 'Duquesne', 'last_name': 'Dukes'}, {'abrv': 'ORST', 'team_id': '450', 'conference': 'Pac-12', 'first_name': 'Oregon State', 'last_name': 'Beavers'}, {'abrv': 'PEPP', 'team_id': '461', 'conference': 'West Coast', 'first_name': 'Pepperdine', 'last_name': 'Waves'}, {'abrv': 'TNST', 'team_id': '582', 'conference': 'Ohio Valley', 'first_name': 'Tennessee State', 'last_name': 'Tigers'}, {'abrv': 'UGA', 'team_id': '230', 'conference': 'Southeastern', 'first_name': 'Georgia', 'last_name': 'Bulldogs'}, {'abrv': 'PROV', 'team_id': '472', 'conference': 'Big East', 'first_name': 'Providence', 'last_name': 'Friars'}, {'abrv': 'CLEM', 'team_id': '120', 'conference': 'Atlantic Coast', 'first_name': 'Clemson', 'last_name': 'Tigers'}, {'abrv': 'SOU', 'team_id': '241', 'conference': 'Southwestern Athletic', 'first_name': 'Southern University', 'last_name': 'Jaguars'}, {'abrv': 'RAD', 'team_id': '483', 'conference': 'Big South', 'first_name': 'Radford', 'last_name': 'Highlanders'}, {'abrv': 'COR', 'team_id': '131', 'conference': 'Ivy League', 'first_name': 'Cornell', 'last_name': 'Big Red'}, {'abrv': 'HOFS', 'team_id': '252', 'conference': 'Colonial', 'first_name': 'Hofstra', 'last_name': 'Pride'}, {'abrv': 'MTST', 'team_id': '373', 'conference': 'Big Sky', 'first_name': 'Montana State', 'last_name': 'Bobcats'}, {'abrv': 'SAC', 'team_id': '494', 'conference': 'Big Sky', 'first_name': 'Sacramento State', 'last_name': 'Hornets'}, {'abrv': 'IDHO', 'team_id': '263', 'conference': 'Big Sky', 'first_name': 'Idaho', 'last_name': 'Vandals'}, {'abrv': 'INST', 'team_id': '274', 'conference': 'Missouri Valley', 'first_name': 'Indiana State', 'last_name': 'Sycamores'}, {'abrv': 'CHAR', 'team_id': '395', 'conference': 'Conference USA', 'first_name': 'Charlotte', 'last_name': '49ers'}, {'abrv': 'DEPL', 'team_id': '164', 'conference': 'Big East', 'first_name': 'DePaul', 'last_name': 'Blue Demons'}, {'abrv': 'LIPS', 'team_id': '1281', 'conference': 'Atlantic Sun', 'first_name': 'Lipscomb', 'last_name': 'Bisons'}, {'abrv': 'BUFF', 'team_id': '71', 'conference': 'Mid-American', 'first_name': 'Buffalo', 'last_name': 'Bulls'}, {'abrv': 'WRIGHT', 'team_id': '660', 'conference': 'Horizon', 'first_name': 'Wright State', 'last_name': 'Raiders'}, {'abrv': 'ULL', 'team_id': '550', 'conference': 'Sun Belt', 'first_name': 'Louisiana', 'last_name': "Ragin' Cajuns"}, {'abrv': 'XAV', 'team_id': '682', 'conference': 'Big East', 'first_name': 'Xavier', 'last_name': 'Musketeers'}, {'abrv': 'FUR', 'team_id': '220', 'conference': 'Southern', 'first_name': 'Furman', 'last_name': 'Paladins'}, {'abrv': 'MRSH', 'team_id': '341', 'conference': 'Conference USA', 'first_name': 'Marshall', 'last_name': 'Thundering Herd'}, {'abrv': 'TNTC', 'team_id': '583', 'conference': 'Ohio Valley', 'first_name': 'Tennessee Tech', 'last_name': 'Golden Eagles'}, {'abrv': 'GA ST', 'team_id': '231', 'conference': 'Sun Belt', 'first_name': 'Georgia State', 'last_name': 'Panthers'}, {'abrv': 'TOL', 'team_id': '594', 'conference': 'Mid-American', 'first_name': 'Toledo', 'last_name': 'Rockets'}, {'abrv': 'CLST', 'team_id': '121', 'conference': 'Horizon', 'first_name': 'Cleveland State', 'last_name': 'Vikings'}, {'abrv': 'MINN', 'team_id': '363', 'conference': 'Big Ten', 'first_name': 'Minnesota', 'last_name': 'Golden Gophers'}, {'abrv': 'HC', 'team_id': '253', 'conference': 'Patriot League', 'first_name': 'Holy Cross', 'last_name': 'Crusaders'}, {'abrv': 'SHSU', 'team_id': '495', 'conference': 'Southland', 'first_name': 'Sam Houston State', 'last_name': 'Bearkats'}, {'abrv': 'IONA', 'team_id': '275', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Iona', 'last_name': 'Gaels'}, {'abrv': 'UNCG', 'team_id': '396', 'conference': 'Southern', 'first_name': 'UNCG', 'last_name': 'Spartans'}, {'abrv': 'DET', 'team_id': '165', 'conference': 'Horizon', 'first_name': 'Detroit', 'last_name': 'Titans'}, {'abrv': 'ETSU', 'team_id': '176', 'conference': 'Southern', 'first_name': 'East Tennessee State', 'last_name': 'Buccaneers'}, {'abrv': 'BAY', 'team_id': '50', 'conference': 'Big 12', 'first_name': 'Baylor', 'last_name': 'Bears'}, {'abrv': 'BGSU', 'team_id': '61', 'conference': 'Mid-American', 'first_name': 'Bowling Green', 'last_name': 'Falcons'}, {'abrv': 'CP', 'team_id': '94', 'conference': 'Big West', 'first_name': 'Cal Poly', 'last_name': 'Mustangs'}, {'abrv': 'WYO', 'team_id': '661', 'conference': 'Mountain West', 'first_name': 'Wyoming', 'last_name': 'Cowboys'}, {'abrv': 'MOST', 'team_id': '551', 'conference': 'Missouri Valley', 'first_name': 'Missouri State', 'last_name': 'Bears'}, {'abrv': 'OAKL', 'team_id': '441', 'conference': 'Horizon', 'first_name': 'Oakland', 'last_name': 'Golden Grizzlies'}, {'abrv': 'FLA', 'team_id': '210', 'conference': 'Southeastern', 'first_name': 'Florida', 'last_name': 'Gators'}, {'abrv': 'FAU', 'team_id': '221', 'conference': 'Conference USA', 'first_name': 'Florida Atlantic', 'last_name': 'Owls'}, {'abrv': 'UTSA', 'team_id': '584', 'conference': 'Conference USA', 'first_name': 'UTSA', 'last_name': 'Roadrunners'}, {'abrv': 'CHSO', 'team_id': '111', 'conference': 'Big South', 'first_name': 'Charleston Southern', 'last_name': 'Buccaneers'}, {'abrv': 'GT', 'team_id': '232', 'conference': 'Atlantic Coast', 'first_name': 'Georgia Tech', 'last_name': 'Yellow Jackets'}, {'abrv': 'PUR', 'team_id': '474', 'conference': 'Big Ten', 'first_name': 'Purdue', 'last_name': 'Boilermakers'}, {'abrv': 'TOWS', 'team_id': '595', 'conference': 'Colonial', 'first_name': 'Towson', 'last_name': 'Tigers'}, {'abrv': 'CCU', 'team_id': '122', 'conference': 'Sun Belt', 'first_name': 'Coastal Carolina', 'last_name': 'Chanticleers'}, {'abrv': 'MVSU', 'team_id': '364', 'conference': 'Southwestern Athletic', 'first_name': 'Mississippi Valley State', 'last_name': 'Delta Devils'}, {'abrv': 'URI', 'team_id': '485', 'conference': 'Atlantic 10', 'first_name': 'Rhode Island', 'last_name': 'Rams'}, {'abrv': 'CREI', 'team_id': '133', 'conference': 'Big East', 'first_name': 'Creighton', 'last_name': 'Bluejays'}, {'abrv': 'HOU', 'team_id': '254', 'conference': 'American', 'first_name': 'Houston', 'last_name': 'Cougars'}, {'abrv': 'MORE', 'team_id': '375', 'conference': 'Ohio Valley', 'first_name': 'Morehead State', 'last_name': 'Eagles'}, {'abrv': 'SAM', 'team_id': '496', 'conference': 'Southern', 'first_name': 'Samford', 'last_name': 'Bulldogs'}, {'abrv': 'IDST', 'team_id': '265', 'conference': 'Big Sky', 'first_name': 'Idaho State', 'last_name': 'Bengals'}, {'abrv': 'DART', 'team_id': '155', 'conference': 'Ivy League', 'first_name': 'Dartmouth', 'last_name': 'Big Green'}, {'abrv': 'IOWA', 'team_id': '276', 'conference': 'Big Ten', 'first_name': 'Iowa', 'last_name': 'Hawkeyes'}, {'abrv': 'KU', 'team_id': '287', 'conference': 'Big 12', 'first_name': 'Kansas', 'last_name': 'Jayhawks'}, {'abrv': 'LAF', 'team_id': '298', 'conference': 'Patriot League', 'first_name': 'Lafayette', 'last_name': 'Leopards'}, {'abrv': 'NORF', 'team_id': '1052', 'conference': 'Mid-Eastern', 'first_name': 'Norfolk State', 'last_name': 'Spartans'}, {'abrv': 'BRAD', 'team_id': '62', 'conference': 'Missouri Valley', 'first_name': 'Bradley', 'last_name': 'Braves'}, {'abrv': 'CAL', 'team_id': '95', 'conference': 'Pac-12', 'first_name': 'California', 'last_name': 'Golden Bears'}, {'abrv': 'WMU', 'team_id': '640', 'conference': 'Mid-American', 'first_name': 'Western Michigan', 'last_name': 'Broncos'}, {'abrv': 'NAU', 'team_id': '420', 'conference': 'Big Sky', 'first_name': 'Northern Arizona', 'last_name': 'Lumberjacks'}, {'abrv': 'AFA', 'team_id': '2', 'conference': 'Mountain West', 'first_name': 'Air Force', 'last_name': 'Falcons'}, {'abrv': 'TXST', 'team_id': '552', 'conference': 'Sun Belt', 'first_name': 'Texas State', 'last_name': 'Bobcats'}, {'abrv': 'FDU', 'team_id': '200', 'conference': 'Northeast', 'first_name': 'Fairleigh Dickinson', 'last_name': 'Knights'}, {'abrv': 'OHIO', 'team_id': '442', 'conference': 'Mid-American', 'first_name': 'Ohio', 'last_name': 'Bobcats'}, {'abrv': 'YALE', 'team_id': '684', 'conference': 'Ivy League', 'first_name': 'Yale', 'last_name': 'Bulldogs'}, {'abrv': 'FAMU', 'team_id': '211', 'conference': 'Mid-Eastern', 'first_name': 'Florida A&M', 'last_name': 'Rattlers'}, {'abrv': 'UMD', 'team_id': '343', 'conference': 'Big Ten', 'first_name': 'Maryland', 'last_name': 'Terrapins'}, {'abrv': 'TEX', 'team_id': '585', 'conference': 'Big 12', 'first_name': 'Texas', 'last_name': 'Longhorns'}, {'abrv': 'CHI ST', 'team_id': '112', 'conference': 'Western Athletic', 'first_name': 'Chicago State', 'last_name': 'Cougars'}, {'abrv': 'GONZ', 'team_id': '233', 'conference': 'West Coast', 'first_name': 'Gonzaga', 'last_name': 'Bulldogs'}, {'abrv': 'TROY', 'team_id': '596', 'conference': 'Sun Belt', 'first_name': 'Troy', 'last_name': 'Trojans'}, {'abrv': 'HART', 'team_id': '244', 'conference': 'America East', 'first_name': 'Hartford', 'last_name': 'Hawks'}, {'abrv': 'MISS', 'team_id': '365', 'conference': 'Southeastern', 'first_name': 'Ole Miss', 'last_name': 'Rebels'}, {'abrv': 'RICE', 'team_id': '486', 'conference': 'Conference USA', 'first_name': 'Rice', 'last_name': 'Owls'}, {'abrv': 'CIT', 'team_id': '134', 'conference': 'Southern', 'first_name': 'Citadel', 'last_name': 'Bulldogs'}, {'abrv': 'HBU', 'team_id': '255', 'conference': 'Southland', 'first_name': 'Houston Baptist', 'last_name': 'Huskies'}, {'abrv': 'MORG', 'team_id': '376', 'conference': 'Mid-Eastern', 'first_name': 'Morgan State', 'last_name': 'Bears'}, {'abrv': 'USD', 'team_id': '497', 'conference': 'West Coast', 'first_name': 'San Diego', 'last_name': 'Toreros'}, {'abrv': 'DAV', 'team_id': '156', 'conference': 'Atlantic 10', 'first_name': 'Davidson', 'last_name': 'Wildcats'}, {'abrv': 'ISU', 'team_id': '277', 'conference': 'Big 12', 'first_name': 'Iowa State', 'last_name': 'Cyclones'}, {'abrv': 'UNCW', 'team_id': '398', 'conference': 'Colonial', 'first_name': 'UNCW', 'last_name': 'Seahawks'}, {'abrv': 'KSU', 'team_id': '288', 'conference': 'Big 12', 'first_name': 'Kansas State', 'last_name': 'Wildcats'}, {'abrv': 'ECU', 'team_id': '178', 'conference': 'American', 'first_name': 'East Carolina', 'last_name': 'Pirates'}, {'abrv': 'LAMR', 'team_id': '299', 'conference': 'Southland', 'first_name': 'Lamar', 'last_name': 'Cardinals'}, {'abrv': 'UCR', 'team_id': '1240', 'conference': 'Big West', 'first_name': 'UC Riverside', 'last_name': 'Highlanders'}, {'abrv': 'UCA', 'team_id': '1262', 'conference': 'Southland', 'first_name': 'Central Arkansas', 'last_name': 'Bears'}, {'abrv': 'FGCU', 'team_id': '1383', 'conference': 'Atlantic Sun', 'first_name': 'FGCU', 'last_name': 'Eagles'}, {'abrv': 'SIUE', 'team_id': '1196', 'conference': 'Ohio Valley', 'first_name': 'SIUE', 'last_name': 'Cougars'}, {'abrv': 'COOK', 'team_id': '52', 'conference': 'Mid-Eastern', 'first_name': 'Bethune-Cookman', 'last_name': 'Wildcats'}, {'abrv': 'CAMP', 'team_id': '96', 'conference': 'Big South', 'first_name': 'Campbell', 'last_name': 'Fighting Camels'}, {'abrv': 'UW', 'team_id': '630', 'conference': 'Pac-12', 'first_name': 'Washington', 'last_name': 'Huskies'}, {'abrv': 'NCAT', 'team_id': '410', 'conference': 'Mid-Eastern', 'first_name': 'North Carolina A&T', 'last_name': 'Aggies'}, {'abrv': 'ST B', 'team_id': '531', 'conference': 'Atlantic 10', 'first_name': 'St. Bonaventure', 'last_name': 'Bonnies'}, {'abrv': 'GBAY', 'team_id': '652', 'conference': 'Horizon', 'first_name': 'Green Bay', 'last_name': 'Phoenix'}, {'abrv': 'NW', 'team_id': '421', 'conference': 'Big Ten', 'first_name': 'Northwestern', 'last_name': 'Wildcats'}, {'abrv': 'AKR', 'team_id': '3', 'conference': 'Mid-American', 'first_name': 'Akron', 'last_name': 'Zips'}, {'abrv': 'LBSU', 'team_id': '311', 'conference': 'Big West', 'first_name': 'Long Beach State', 'last_name': 'Beach'}, {'abrv': 'SYR', 'team_id': '553', 'conference': 'Atlantic Coast', 'first_name': 'Syracuse', 'last_name': 'Orange'}, {'abrv': 'FAIR', 'team_id': '201', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Fairfield', 'last_name': 'Stags'}, {'abrv': 'OSU', 'team_id': '443', 'conference': 'Big Ten', 'first_name': 'Ohio State', 'last_name': 'Buckeyes'}, {'abrv': 'YSU', 'team_id': '685', 'conference': 'Horizon', 'first_name': 'Youngstown State', 'last_name': 'Penguins'}, {'abrv': 'FIU', 'team_id': '212', 'conference': 'Conference USA', 'first_name': 'FIU', 'last_name': 'Panthers'}, {'abrv': 'CCSU', 'team_id': '102', 'conference': 'Northeast', 'first_name': 'Central Connecticut State', 'last_name': 'Blue Devils'}, {'abrv': 'UMASS', 'team_id': '344', 'conference': 'Atlantic 10', 'first_name': 'Massachusetts', 'last_name': 'Minutemen'}, {'abrv': 'PITT', 'team_id': '465', 'conference': 'Atlantic Coast', 'first_name': 'Pittsburgh', 'last_name': 'Panthers'}, {'abrv': 'GRAM', 'team_id': '234', 'conference': 'Southwestern Athletic', 'first_name': 'Grambling State', 'last_name': 'Tigers'}, {'abrv': 'MIA', 'team_id': '355', 'conference': 'Atlantic Coast', 'first_name': 'Miami (FL)', 'last_name': 'Hurricanes'}, {'abrv': 'COLG', 'team_id': '124', 'conference': 'Patriot League', 'first_name': 'Colgate', 'last_name': 'Raiders'}, {'abrv': 'HARV', 'team_id': '245', 'conference': 'Ivy League', 'first_name': 'Harvard', 'last_name': 'Crimson'}, {'abrv': 'MSST', 'team_id': '366', 'conference': 'Southeastern', 'first_name': 'Mississippi State', 'last_name': 'Bulldogs'}, {'abrv': 'RICH', 'team_id': '487', 'conference': 'Atlantic 10', 'first_name': 'Richmond', 'last_name': 'Spiders'}, {'abrv': 'HOW', 'team_id': '256', 'conference': 'Mid-Eastern', 'first_name': 'Howard', 'last_name': 'Bison'}, {'abrv': 'SDSU', 'team_id': '498', 'conference': 'Mountain West', 'first_name': 'San Diego State', 'last_name': 'Aztecs'}, {'abrv': 'ILL', 'team_id': '267', 'conference': 'Big Ten', 'first_name': 'Illinois', 'last_name': 'Fighting Illini'}, {'abrv': 'DAY', 'team_id': '157', 'conference': 'Atlantic 10', 'first_name': 'Dayton', 'last_name': 'Flyers'}, {'abrv': 'ULM', 'team_id': '399', 'conference': 'Sun Belt', 'first_name': 'Louisiana-Monroe', 'last_name': 'Warhawks'}, {'abrv': 'EIU', 'team_id': '179', 'conference': 'Ohio Valley', 'first_name': 'Eastern Illinois', 'last_name': 'Panthers'}, {'abrv': 'SDSU', 'team_id': '1472', 'conference': 'Summit', 'first_name': 'South Dakota State', 'last_name': 'Jackrabbits'}, {'abrv': 'UALR', 'team_id': '20', 'conference': 'Sun Belt', 'first_name': 'Little Rock', 'last_name': 'Trojans'}, {'abrv': 'NJIT', 'team_id': '1186', 'conference': 'Atlantic Sun', 'first_name': 'NJIT', 'last_name': 'Highlanders'}, {'abrv': 'BRWN', 'team_id': '64', 'conference': 'Ivy League', 'first_name': 'Brown', 'last_name': 'Bears'}, {'abrv': 'CANI', 'team_id': '97', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Canisius', 'last_name': 'Golden Griffins'}, {'abrv': 'VT', 'team_id': '620', 'conference': 'Atlantic Coast', 'first_name': 'Virginia Tech', 'last_name': 'Hokies'}, {'abrv': 'NEB', 'team_id': '400', 'conference': 'Big Ten', 'first_name': 'Nebraska', 'last_name': 'Cornhuskers'}, {'abrv': 'USM', 'team_id': '521', 'conference': 'Conference USA', 'first_name': 'Southern Miss', 'last_name': 'Golden Eagles'}, {'abrv': 'NCST', 'team_id': '411', 'conference': 'Atlantic Coast', 'first_name': 'North Carolina State', 'last_name': 'Wolfpack'}, {'abrv': 'STF NY', 'team_id': '532', 'conference': 'Northeast', 'first_name': 'St. Francis Brooklyn', 'last_name': 'Terriers'}, {'abrv': 'LA S', 'team_id': '301', 'conference': 'Atlantic 10', 'first_name': 'La Salle', 'last_name': 'Explorers'}, {'abrv': 'NWST', 'team_id': '422', 'conference': 'Southland', 'first_name': 'Northwestern State', 'last_name': 'Demons'}, {'abrv': 'STP', 'team_id': '543', 'conference': 'Metro Atlantic Athletic', 'first_name': "Saint Peter's", 'last_name': 'Peacocks'}, {'abrv': 'OU', 'team_id': '444', 'conference': 'Big 12', 'first_name': 'Oklahoma', 'last_name': 'Sooners'}, {'abrv': 'FSU', 'team_id': '213', 'conference': 'Atlantic Coast', 'first_name': 'Florida State', 'last_name': 'Seminoles'}, {'abrv': 'MAINE', 'team_id': '334', 'conference': 'America East', 'first_name': 'Maine', 'last_name': 'Black Bears'}, {'abrv': 'UOP', 'team_id': '455', 'conference': 'West Coast', 'first_name': 'Pacific', 'last_name': 'Tigers'}, {'abrv': 'TCU', 'team_id': '576', 'conference': 'Big 12', 'first_name': 'TCU', 'last_name': 'Horned Frogs'}, {'abrv': 'UCF', 'team_id': '103', 'conference': 'American', 'first_name': 'UCF', 'last_name': 'Knights'}, {'abrv': 'MCNS', 'team_id': '345', 'conference': 'Southland', 'first_name': 'McNeese State', 'last_name': 'Cowboys'}, {'abrv': 'TAMU', 'team_id': '587', 'conference': 'Southeastern', 'first_name': 'Texas A&M', 'last_name': 'Aggies'}, {'abrv': 'M-OH', 'team_id': '356', 'conference': 'Mid-American', 'first_name': 'Miami (OH)', 'last_name': 'RedHawks'}, {'abrv': 'TULN', 'team_id': '598', 'conference': 'American', 'first_name': 'Tulane', 'last_name': 'Green Wave'}, {'abrv': 'COLO', 'team_id': '125', 'conference': 'Pac-12', 'first_name': 'Colorado', 'last_name': 'Buffaloes'}, {'abrv': 'HAW', 'team_id': '246', 'conference': 'Big West', 'first_name': 'Hawaii', 'last_name': 'Rainbow Warriors'}, {'abrv': 'MIZZ', 'team_id': '367', 'conference': 'Southeastern', 'first_name': 'Missouri', 'last_name': 'Tigers'}, {'abrv': 'RID', 'team_id': '488', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Rider', 'last_name': 'Broncs'}, {'abrv': 'MSM', 'team_id': '378', 'conference': 'Northeast', 'first_name': "Mount St. Mary's", 'last_name': 'Mountaineers'}, {'abrv': 'SAN F', 'team_id': '499', 'conference': 'West Coast', 'first_name': 'San Francisco', 'last_name': 'Dons'}, {'abrv': 'UIC', 'team_id': '268', 'conference': 'Horizon', 'first_name': 'UIC', 'last_name': 'Flames'}, {'abrv': 'TAMUCC', 'team_id': '1231', 'conference': 'Southland', 'first_name': 'Texas A&M-Corpus Christi', 'last_name': 'Islanders'}, {'abrv': 'BRYT', 'team_id': '1594', 'conference': 'Northeast', 'first_name': 'Bryant', 'last_name': 'Bulldogs'}, {'abrv': 'KENN', 'team_id': '1374', 'conference': 'Atlantic Sun', 'first_name': 'Kennesaw State', 'last_name': 'Owls'}, {'abrv': 'PRST', 'team_id': '1033', 'conference': 'Big Sky', 'first_name': 'Portland State', 'last_name': 'Vikings'}, {'abrv': 'ALCN', 'team_id': '10', 'conference': 'Southwestern Athletic', 'first_name': 'Alcorn State', 'last_name': 'Braves'}, {'abrv': 'BING', 'team_id': '1286', 'conference': 'America East', 'first_name': 'Binghamton', 'last_name': 'Bearcats'}, {'abrv': 'ALBY', 'team_id': '1176', 'conference': 'America East', 'first_name': 'Albany', 'last_name': 'Great Danes'}, {'abrv': 'PEAY', 'team_id': '32', 'conference': 'Ohio Valley', 'first_name': 'Austin Peay', 'last_name': 'Governors'}, {'abrv': 'UTAH', 'team_id': '610', 'conference': 'Pac-12', 'first_name': 'Utah', 'last_name': "Runnin' Utes"}, {'abrv': 'SJSU', 'team_id': '500', 'conference': 'Mountain West', 'first_name': 'San Jose State', 'last_name': 'Spartans'}, {'abrv': 'VMI', 'team_id': '621', 'conference': 'Southern', 'first_name': 'VMI', 'last_name': 'Keydets'}, {'abrv': 'WSU', 'team_id': '632', 'conference': 'Pac-12', 'first_name': 'Washington State', 'last_name': 'Cougars'}, {'abrv': 'UNLV', 'team_id': '401', 'conference': 'Mountain West', 'first_name': 'UNLV', 'last_name': "Runnin' Rebels"}, {'abrv': 'SUU', 'team_id': '522', 'conference': 'Big Sky', 'first_name': 'Southern Utah', 'last_name': 'Thunderbirds'}, {'abrv': 'SFU', 'team_id': '533', 'conference': 'Northeast', 'first_name': 'Saint Francis U', 'last_name': 'Red Flash'}, {'abrv': 'MILW', 'team_id': '654', 'conference': 'Horizon', 'first_name': 'Milwaukee', 'last_name': 'Panthers'}, {'abrv': 'ND', 'team_id': '423', 'conference': 'Atlantic Coast', 'first_name': 'Notre Dame', 'last_name': 'Fighting Irish'}, {'abrv': 'LT', 'team_id': '313', 'conference': 'Conference USA', 'first_name': 'Louisiana Tech', 'last_name': 'Bulldogs'}, {'abrv': 'N FLA', 'team_id': '434', 'conference': 'Atlantic Sun', 'first_name': 'North Florida', 'last_name': 'Ospreys'}, {'abrv': 'FOR', 'team_id': '214', 'conference': 'Atlantic 10', 'first_name': 'Fordham', 'last_name': 'Rams'}, {'abrv': 'MANH', 'team_id': '335', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Manhattan', 'last_name': 'Jaspers'}, {'abrv': 'TEM', 'team_id': '577', 'conference': 'American', 'first_name': 'Temple', 'last_name': 'Owls'}, {'abrv': 'CMU', 'team_id': '104', 'conference': 'Mid-American', 'first_name': 'Central Michigan', 'last_name': 'Chippewas'}, {'abrv': 'UMBC', 'team_id': '346', 'conference': 'America East', 'first_name': 'UMBC', 'last_name': 'Retrievers'}, {'abrv': 'PORT', 'team_id': '467', 'conference': 'West Coast', 'first_name': 'Portland', 'last_name': 'Pilots'}, {'abrv': 'UTA', 'team_id': '588', 'conference': 'Sun Belt', 'first_name': 'UT Arlington', 'last_name': 'Mavericks'}, {'abrv': 'MICH', 'team_id': '357', 'conference': 'Big Ten', 'first_name': 'Michigan', 'last_name': 'Wolverines'}, {'abrv': 'TLSA', 'team_id': '599', 'conference': 'American', 'first_name': 'Tulsa', 'last_name': 'Golden Hurricane'}, {'abrv': 'CSU', 'team_id': '126', 'conference': 'Mountain West', 'first_name': 'Colorado State', 'last_name': 'Rams'}, {'abrv': 'UMKC', 'team_id': '368', 'conference': 'Western Athletic', 'first_name': 'Kansas City', 'last_name': 'Roos'}, {'abrv': 'RMU', 'team_id': '489', 'conference': 'Northeast', 'first_name': 'Robert Morris', 'last_name': 'Colonials'}, {'abrv': 'ILST', 'team_id': '269', 'conference': 'Missouri Valley', 'first_name': 'Illinois State', 'last_name': 'Redbirds'}, {'abrv': 'DEL', 'team_id': '159', 'conference': 'Colonial', 'first_name': 'Delaware', 'last_name': "Fightin' Blue Hens"}, {'abrv': 'ARST', 'team_id': '22', 'conference': 'Sun Belt', 'first_name': 'Arkansas State', 'last_name': 'Red Wolves'}, {'abrv': 'BUCK', 'team_id': '66', 'conference': 'Patriot League', 'first_name': 'Bucknell', 'last_name': 'Bison'}, {'abrv': 'UCD', 'team_id': '88', 'conference': 'Big West', 'first_name': 'UC Davis', 'last_name': 'Aggies'}, {'abrv': 'USU', 'team_id': '611', 'conference': 'Mountain West', 'first_name': 'Utah State', 'last_name': 'Aggies'}, {'abrv': 'UCSB', 'team_id': '501', 'conference': 'Big West', 'first_name': 'UC Santa Barbara', 'last_name': 'Gauchos'}, {'abrv': 'SIEN', 'team_id': '512', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Siena', 'last_name': 'Saints'}, {'abrv': 'WEB', 'team_id': '633', 'conference': 'Big Sky', 'first_name': 'Weber State', 'last_name': 'Wildcats'}, {'abrv': 'NEV', 'team_id': '402', 'conference': 'Mountain West', 'first_name': 'Nevada', 'last_name': 'Wolf Pack'}, {'abrv': 'WCU', 'team_id': '644', 'conference': 'Southern', 'first_name': 'Western Carolina', 'last_name': 'Catamounts'}, {'abrv': 'UNC', 'team_id': '413', 'conference': 'Atlantic Coast', 'first_name': 'North Carolina', 'last_name': 'Tar Heels'}, {'abrv': 'ST JN', 'team_id': '534', 'conference': 'Big East', 'first_name': "St. John's", 'last_name': 'Red Storm'}, {'abrv': 'LEH', 'team_id': '303', 'conference': 'Patriot League', 'first_name': 'Lehigh', 'last_name': 'Mountain Hawks'}, {'abrv': 'STAN', 'team_id': '545', 'conference': 'Pac-12', 'first_name': 'Stanford', 'last_name': 'Cardinal'}, {'abrv': 'ALA', 'team_id': '6', 'conference': 'Southeastern', 'first_name': 'Alabama', 'last_name': 'Crimson Tide'}, {'abrv': 'LOU', 'team_id': '314', 'conference': 'Atlantic Coast', 'first_name': 'Louisville', 'last_name': 'Cardinals'}, {'abrv': 'OKST', 'team_id': '446', 'conference': 'Big 12', 'first_name': 'Oklahoma State', 'last_name': 'Cowboys'}, {'abrv': 'UTM', 'team_id': '578', 'conference': 'Ohio Valley', 'first_name': 'UT Martin', 'last_name': 'Skyhawks'}, {'abrv': 'GASO', 'team_id': '226', 'conference': 'Sun Belt', 'first_name': 'Georgia Southern', 'last_name': 'Eagles'}, {'abrv': 'UMES', 'team_id': '347', 'conference': 'Mid-Eastern', 'first_name': 'Maryland Eastern Shore', 'last_name': 'Hawks'}, {'abrv': 'PV', 'team_id': '468', 'conference': 'Southwestern Athletic', 'first_name': 'Prairie View A&M', 'last_name': 'Panthers'}, {'abrv': 'UTEP', 'team_id': '589', 'conference': 'Conference USA', 'first_name': 'UTEP', 'last_name': 'Miners'}, {'abrv': 'CIN', 'team_id': '116', 'conference': 'American', 'first_name': 'Cincinnati', 'last_name': 'Bearcats'}, {'abrv': 'GCANYO', 'team_id': '237', 'conference': 'Western Athletic', 'first_name': 'Grand Canyon', 'last_name': 'Antelopes'}, {'abrv': 'MSU', 'team_id': '358', 'conference': 'Big Ten', 'first_name': 'Michigan State', 'last_name': 'Spartans'}, {'abrv': 'CLMB', 'team_id': '127', 'conference': 'Ivy League', 'first_name': 'Columbia', 'last_name': 'Lions'}, {'abrv': 'HI PT', 'team_id': '1112', 'conference': 'Big South', 'first_name': 'High Point', 'last_name': 'Panthers'}, {'abrv': 'UAB', 'team_id': '34', 'conference': 'Conference USA', 'first_name': 'UAB', 'last_name': 'Blazers'}, {'abrv': 'BUT', 'team_id': '67', 'conference': 'Big East', 'first_name': 'Butler', 'last_name': 'Bulldogs'}, {'abrv': 'UT R', 'team_id': '601', 'conference': 'Western Athletic', 'first_name': 'UT Rio Grande Valley', 'last_name': 'Vaqueros'}, {'abrv': 'UCI', 'team_id': '89', 'conference': 'Big West', 'first_name': 'UC Irvine', 'last_name': 'Anteaters'}, {'abrv': 'SCU', 'team_id': '502', 'conference': 'West Coast', 'first_name': 'Santa Clara', 'last_name': 'Broncos'}, {'abrv': 'UNH', 'team_id': '403', 'conference': 'America East', 'first_name': 'New Hampshire', 'last_name': 'Wildcats'}, {'abrv': 'S ALA', 'team_id': '524', 'conference': 'Sun Belt', 'first_name': 'South Alabama', 'last_name': 'Jaguars'}, {'abrv': 'ST JO', 'team_id': '535', 'conference': 'Atlantic 10', 'first_name': "Saint Joseph's", 'last_name': 'Hawks'}, {'abrv': 'UNCO', 'team_id': '425', 'conference': 'Big Sky', 'first_name': 'Northern Colorado', 'last_name': 'Bears'}, {'abrv': 'ODU', 'team_id': '447', 'conference': 'Conference USA', 'first_name': 'Old Dominion', 'last_name': 'Monarchs'}, {'abrv': 'GEO W', 'team_id': '227', 'conference': 'Atlantic 10', 'first_name': 'George Washington', 'last_name': 'Colonials'}, {'abrv': 'MTSU', 'team_id': '359', 'conference': 'Conference USA', 'first_name': 'Middle Tennessee', 'last_name': 'Blue Raiders'}, {'abrv': 'ARMY', 'team_id': '24', 'conference': 'Patriot League', 'first_name': 'Army West Point', 'last_name': 'Black Knights'}, {'abrv': 'ARPB', 'team_id': '35', 'conference': 'Southwestern Athletic', 'first_name': 'UAPB', 'last_name': 'Golden Lions'}, {'abrv': 'BALL', 'team_id': '46', 'conference': 'Mid-American', 'first_name': 'Ball State', 'last_name': 'Cardinals'}, {'abrv': 'IPFW', 'team_id': '932', 'conference': 'Summit', 'first_name': 'Purdue Fort Wayne', 'last_name': 'Mastodons'}, {'abrv': 'BSU', 'team_id': '57', 'conference': 'Mountain West', 'first_name': 'Boise State', 'last_name': 'Broncos'}, {'abrv': 'BYU', 'team_id': '68', 'conference': 'West Coast', 'first_name': 'BYU', 'last_name': 'Cougars'}, {'abrv': 'VCU', 'team_id': '613', 'conference': 'Atlantic 10', 'first_name': 'VCU', 'last_name': 'Rams'}, {'abrv': 'UNM', 'team_id': '404', 'conference': 'Mountain West', 'first_name': 'New Mexico', 'last_name': 'Lobos'}, {'abrv': 'SC', 'team_id': '525', 'conference': 'Southeastern', 'first_name': 'South Carolina', 'last_name': 'Gamecocks'}, {'abrv': 'UNT', 'team_id': '415', 'conference': 'Conference USA', 'first_name': 'North Texas', 'last_name': 'Mean Green'}, {'abrv': 'ST L', 'team_id': '536', 'conference': 'Atlantic 10', 'first_name': 'Saint Louis', 'last_name': 'Billikens'}, {'abrv': 'WIS', 'team_id': '657', 'conference': 'Big Ten', 'first_name': 'Wisconsin', 'last_name': 'Badgers'}, {'abrv': 'SFA', 'team_id': '547', 'conference': 'Southland', 'first_name': 'Stephen F. Austin', 'last_name': 'Lumberjacks'}, {'abrv': 'ALST', 'team_id': '8', 'conference': 'Southwestern Athletic', 'first_name': 'Alabama State', 'last_name': 'Hornets'}, {'abrv': 'LOY CH', 'team_id': '316', 'conference': 'Missouri Valley', 'first_name': 'Loyola Chicago', 'last_name': 'Ramblers'}, {'abrv': 'ORU', 'team_id': '448', 'conference': 'Summit', 'first_name': 'Oral Roberts', 'last_name': 'Golden Eagles'}, {'abrv': 'STONY', 'team_id': '569', 'conference': 'America East', 'first_name': 'Stony Brook', 'last_name': 'Seawolves'}, {'abrv': 'FRES', 'team_id': '217', 'conference': 'Mountain West', 'first_name': 'Fresno State', 'last_name': 'Bulldogs'}, {'abrv': 'MRST', 'team_id': '338', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Marist', 'last_name': 'Red Foxes'}, {'abrv': 'PSU', 'team_id': '459', 'conference': 'Big Ten', 'first_name': 'Penn State', 'last_name': 'Nittany Lions'}, {'abrv': 'COFC', 'team_id': '107', 'conference': 'Colonial', 'first_name': 'Charleston', 'last_name': 'Cougars'}, {'abrv': 'GEO M', 'team_id': '228', 'conference': 'Atlantic 10', 'first_name': 'George Mason', 'last_name': 'Patriots'}, {'abrv': 'MEM', 'team_id': '349', 'conference': 'American', 'first_name': 'Memphis', 'last_name': 'Tigers'}, {'abrv': 'CONN', 'team_id': '129', 'conference': 'American', 'first_name': 'UConn', 'last_name': 'Huskies'}, {'abrv': 'NAL', 'team_id': '1333', 'conference': 'Atlantic Sun', 'first_name': 'North Alabama', 'last_name': 'Lions'}, {'abrv': 'AAMU', 'team_id': '1037', 'conference': 'Southwestern Athletic', 'first_name': 'Alabama A&M', 'last_name': 'Bulldogs'}, {'abrv': 'UND', 'team_id': '1279', 'conference': 'Summit', 'first_name': 'North Dakota', 'last_name': 'Fighting Hawks'}, {'abrv': 'AMER', 'team_id': '14', 'conference': 'Patriot League', 'first_name': 'American University', 'last_name': 'Eagles'}, {'abrv': 'WEBB', 'team_id': '1048', 'conference': 'Big South', 'first_name': 'Gardner-Webb', 'last_name': "Runnin' Bulldogs"}, {'abrv': 'ACU', 'team_id': '36', 'conference': 'Southland', 'first_name': 'Abilene Christian', 'last_name': 'Wildcats'}, {'abrv': 'BELM', 'team_id': '47', 'conference': 'Ohio Valley', 'first_name': 'Belmont', 'last_name': 'Bruins'}, {'abrv': 'BC', 'team_id': '58', 'conference': 'Atlantic Coast', 'first_name': 'Boston College', 'last_name': 'Eagles'}, {'abrv': 'HAMP', 'team_id': '702', 'conference': 'Big South', 'first_name': 'Hampton', 'last_name': 'Pirates'}, {'abrv': 'VALP', 'team_id': '614', 'conference': 'Missouri Valley', 'first_name': 'Valparaiso', 'last_name': 'Crusaders'}, {'abrv': 'SMU', 'team_id': '515', 'conference': 'American', 'first_name': 'SMU', 'last_name': 'Mustangs'}, {'abrv': 'WVU', 'team_id': '636', 'conference': 'Big 12', 'first_name': 'West Virginia', 'last_name': 'Mountaineers'}, {'abrv': 'NMSU', 'team_id': '405', 'conference': 'Western Athletic', 'first_name': 'New Mexico State', 'last_name': 'Aggies'}, {'abrv': 'S FLA', 'team_id': '526', 'conference': 'American', 'first_name': 'South Florida', 'last_name': 'Bulls'}, {'abrv': 'N.E.', 'team_id': '416', 'conference': 'Colonial', 'first_name': 'Northeastern', 'last_name': 'Huskies'}, {'abrv': 'W&M', 'team_id': '658', 'conference': 'Colonial', 'first_name': 'William & Mary', 'last_name': 'Tribe'}, {'abrv': 'LIB', 'team_id': '306', 'conference': 'Atlantic Sun', 'first_name': 'Liberty', 'last_name': 'Flames'}, {'abrv': 'STET', 'team_id': '548', 'conference': 'Atlantic Sun', 'first_name': 'Stetson', 'last_name': 'Hatters'}, {'abrv': 'LMU', 'team_id': '317', 'conference': 'West Coast', 'first_name': 'Loyola Marymount', 'last_name': 'Lions'}, {'abrv': 'ORE', 'team_id': '449', 'conference': 'Pac-12', 'first_name': 'Oregon', 'last_name': 'Ducks'}, {'abrv': 'MARQ', 'team_id': '339', 'conference': 'Big East', 'first_name': 'Marquette', 'last_name': 'Golden Eagles'}, {'abrv': 'GTWN', 'team_id': '229', 'conference': 'Big East', 'first_name': 'Georgetown', 'last_name': 'Hoyas'}, {'abrv': 'MALO', 'team_id': '1543', 'conference': 'America East', 'first_name': 'UMass Lowell', 'last_name': 'River Hawks'}, {'abrv': 'NDSU', 'team_id': '1455', 'conference': 'Summit', 'first_name': 'North Dakota State', 'last_name': 'Bison'}, {'abrv': 'QUIN', 'team_id': '1115', 'conference': 'Metro Atlantic Athletic', 'first_name': 'Quinnipiac', 'last_name': 'Bobcats'}, {'abrv': 'BOS U', 'team_id': '59', 'conference': 'Patriot League', 'first_name': 'Boston University', 'last_name': 'Terriers'}, {'abrv': 'VAN', 'team_id': '615', 'conference': 'Southeastern', 'first_name': 'Vanderbilt', 'last_name': 'Commodores'}, {'abrv': 'UNO', 'team_id': '406', 'conference': 'Southland', 'first_name': 'New Orleans', 'last_name': 'Privateers'}, {'abrv': 'WICH', 'team_id': '648', 'conference': 'American', 'first_name': 'Wichita State', 'last_name': 'Shockers'}, {'abrv': 'NIU', 'team_id': '417', 'conference': 'Mid-American', 'first_name': 'Northern Illinois', 'last_name': 'Huskies'}, {'abrv': 'ST M', 'team_id': '538', 'conference': 'West Coast', 'first_name': "Saint Mary's", 'last_name': 'Gaels'}, {'abrv': 'WOF', 'team_id': '659', 'conference': 'Southern', 'first_name': 'Wofford', 'last_name': 'Terriers'}, {'abrv': 'LOY MD', 'team_id': '318', 'conference': 'Patriot League', 'first_name': 'Loyola Maryland', 'last_name': 'Greyhounds'}, {'abrv': 'CSF', 'team_id': '219', 'conference': 'Big West', 'first_name': 'Cal State Fullerton', 'last_name': 'Titans'}, {'abrv': 'USCU', 'team_id': '1203', 'conference': 'Big South', 'first_name': 'USC Upstate', 'last_name': 'Spartans'}]


class NCAABDB(DB):

    dbPath = os.environ["HOME"]+"/Yahoo/ncaab/ncaab.db"

    def __init__(self):
        super().__init__(self.dbPath)


    def getTableList(self):
        return (gamesTable, colTeamsTable, colPlayersTable, gameLinesTable, overUndersTable,
                lineupsTable, playerStatsTable, teamStatsTable, positionsTypeTable)
                # dkYahooTable, dkTeamTable, dkSheetTable, dkSheetGamesTable, dkPriceTable)


    def seed(self):

        for position in positions:
            self.insert(positionsTypeTable, info=position)

        for team in teams:
            self.insert(colTeamsTable, info=team)

        self.commit()
