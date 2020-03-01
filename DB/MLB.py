import os
import sqlite3
import re
import datetime
import unicodedata

from itertools import chain

from .Database import Database as DB, Table as TB
from ..Utils import ResultsParse as RP

# for debugging
from pprint import pprint

################################################################################
################################################################################

def yId(yahooId):
    try:
        return yahooId.split(".")[-1]
    except AttributeError:
        return "-1"


def normal(name):
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    return name


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
proPlayersTable.addCol("first_name", "TEXT")
proPlayersTable.addCol("last_name", "TEXT")
proPlayersTable.addCol("height", "INT", True)
proPlayersTable.addCol("weight", "INT", True)
proPlayersTable.addCol("bats", "TEXT")
proPlayersTable.addCol("throws", "TEXT")
proPlayersTable.addCol("rookie_season", "INT", True)
proPlayersTable.addCol("birth_year", "INT", True)
proPlayersTable.addCol("birth_day", "REAL", True)
    ## Table Indexes
proPlayersTable.addIndex("names", "last_name, first_name")
proPlayersTable.addIndex("throws", "throws")
proPlayersTable.addIndex("bats", "bats")
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


### Stadiums Table
stadiumsTable = TB("stadiums")
    ### Primary Key
stadiumsTable.addPk("stadium_id", "INT")
    ## Table Cols
stadiumsTable.addCol("title", "TEXT")
###############


### BatterStats Table
batterStatsTable = TB("batter_stats")
    ### Primary Key
batterStatsTable.addPk("batter_stat_id", "INT")
    ### Foreign Key
batterStatsTable.addFk("game_id", "games", "game_id")
batterStatsTable.addFk("player_id", "pro_players", "player_id")
batterStatsTable.addFk("team_id", "pro_teams", "team_id")
batterStatsTable.addFk("opp_id", "pro_teams", "team_id")
    ## Table Cols
batterStatsTable.addCol("pa", "INT")
batterStatsTable.addCol("ab", "INT")
batterStatsTable.addCol("bb", "INT")
batterStatsTable.addCol("r", "INT")
batterStatsTable.addCol("h", "INT")
batterStatsTable.addCol("dbl", "INT")
batterStatsTable.addCol("tpl", "INT")
batterStatsTable.addCol("hr", "INT")
batterStatsTable.addCol("tb", "INT")
batterStatsTable.addCol("rbi", "INT")
batterStatsTable.addCol("sb", "INT")
batterStatsTable.addCol("so", "INT")
batterStatsTable.addCol("lob", "INT")
batterStatsTable.addCol("hbp", "INT")
    ## Table Indexes
batterStatsTable.addIndex("player_batter_stats", "player_id, game_id")
###############


### Pitcher Stats Table
pitcherStatsTable = TB("pitcher_stats")
    ### Primary Key
pitcherStatsTable.addPk("pitcher_stat_id", "INT")
    ### Foreign Key
pitcherStatsTable.addFk("game_id", "games", "game_id")
pitcherStatsTable.addFk("player_id", "pro_players", "player_id")
pitcherStatsTable.addFk("team_id", "pro_teams", "team_id")
pitcherStatsTable.addFk("opp_id", "pro_teams", "team_id")
    ## Table Cols
pitcherStatsTable.addCol("ip", "REAL")
pitcherStatsTable.addCol("tot", "INT")
pitcherStatsTable.addCol("strikes", "INT")
pitcherStatsTable.addCol("gb", "INT")
pitcherStatsTable.addCol("fb", "INT")
pitcherStatsTable.addCol("bba", "INT")
pitcherStatsTable.addCol("ha", "INT")
pitcherStatsTable.addCol("ra", "INT")
pitcherStatsTable.addCol("er", "INT")
pitcherStatsTable.addCol("k", "INT")
pitcherStatsTable.addCol("hra", "INT")
pitcherStatsTable.addCol("hbp", "INT")
pitcherStatsTable.addCol("w", "INT")
pitcherStatsTable.addCol("l", "INT")
pitcherStatsTable.addCol("sv", "INT")
pitcherStatsTable.addCol("blsv", "INT")
    ## Table Indexes
pitcherStatsTable.addIndex("player_pitcher_stats", "player_id, game_id")
###############


### Team Stats Table
teamStatsTable = TB("team_stats")
    ### Primary Key
teamStatsTable.addPk("team_stats_id", "INT")
    ### Foreign Key
teamStatsTable.addFk("game_id", "games", "game_id")
teamStatsTable.addFk("team_id", "pro_teams", "team_id")
teamStatsTable.addFk("opp_id", "pro_teams", "team_id")
    ## Table Cols
teamStatsTable.addCol("pa", "INT")
teamStatsTable.addCol("ab", "INT")
teamStatsTable.addCol("bb", "INT")
teamStatsTable.addCol("r", "INT")
teamStatsTable.addCol("h", "INT")
teamStatsTable.addCol("dbl", "INT")
teamStatsTable.addCol("tpl", "INT")
teamStatsTable.addCol("hr", "INT")
teamStatsTable.addCol("tb", "INT")
teamStatsTable.addCol("rbi", "INT")
teamStatsTable.addCol("sb", "INT")
teamStatsTable.addCol("cs", "INT")
teamStatsTable.addCol("so", "INT")
teamStatsTable.addCol("lob", "INT")
teamStatsTable.addCol("hbp", "INT")
teamStatsTable.addCol("ip", "REAL")
teamStatsTable.addCol("tot", "INT")
teamStatsTable.addCol("strikes", "INT")
teamStatsTable.addCol("gb", "INT")
teamStatsTable.addCol("fb", "INT")
teamStatsTable.addCol("bba", "INT")
teamStatsTable.addCol("ha", "INT")
teamStatsTable.addCol("ra", "INT")
teamStatsTable.addCol("er", "INT")
teamStatsTable.addCol("k", "INT")
teamStatsTable.addCol("hra", "INT")
    ## Table Indexes
teamStatsTable.addIndex("team_game_stats", "team_id, game_id")
teamStatsTable.addIndex("opp_game_stats", "opp_id, game_id")
###############



### StatTypes Table
statTypesTable = TB("stat_types")
    ### Primary Key
statTypesTable.addPk("stat_id", "INT")
    ## Table Cols
statTypesTable.addCol("title", "TEXT")
statTypesTable.addCol("abrv", "TEXT")
###############



### PitchTypes Table
pitchTypesTable = TB("pitch_types")
    ### Primary Key
pitchTypesTable.addPk("pitch_type_id", "INT")
    ## Table Cols
pitchTypesTable.addCol("title", "TEXT")
###############


### PitchResults Table
pitchResultsTable = TB("pitch_results")
    ### Primary Key
pitchResultsTable.addPk("pitch_result_id", "INT")
    ## Table Cols
pitchResultsTable.addCol("title", "TEXT")
###############


### PitchLocations Table
pitchLocationsTable = TB("pitch_locations")
    ### Primary Key
pitchLocationsTable.addPk("pitch_location_id", "INT")
    ## Table Cols
pitchLocationsTable.addCol("x_value", "INT")
pitchLocationsTable.addCol("y_value", "INT")
pitchLocationsTable.addCol("box", "INT")
pitchLocationsTable.addCol("strike_zone", "INT")
    ## Table Indexes
pitchLocationsTable.addIndex("x_y", "x_value, y_value")
###############


### Pitches Table
pitchesTable = TB("pitches")
    ### Primary Key
pitchesTable.addPk("pitch_id","INT")
    ## Foreign Keys
pitchesTable.addFk("game_id", "games", "game_id")
pitchesTable.addFk("pitcher_id", "pro_players", "player_id")
pitchesTable.addFk("batter_id", "pro_players", "player_id")
pitchesTable.addFk("pitch_type_id", "pitch_types", "pitch_type_id")
pitchesTable.addFk("pitch_location_id", "pitch_locations", "pitch_location_id")
pitchesTable.addFk("pitch_result_id", "pitch_results", "pitch_result_id")
    ### Table Cols
pitchesTable.addCol("play_num", "INT")
pitchesTable.addCol("pitch_num", "INT")
pitchesTable.addCol("balls", "INT")
pitchesTable.addCol("strikes", "INT")
pitchesTable.addCol("sequence", "INT")
pitchesTable.addCol("pitch_velocity", "INT")
    ### Table Indexes
pitchesTable.addIndex("pitcher_pitch", "pitcher_id, game_id")
pitchesTable.addIndex("batter_pitch", "batter_id, game_id")
###############


### PitchContacts Table
atBatResultsTable = TB("ab_results")
    ### Primary Key
atBatResultsTable.addPk("ab_result_id","INT")
    ## Foreign Keys
atBatResultsTable.addFk("game_id", "games", "game_id")
atBatResultsTable.addFk("pitcher_id", "pro_players", "player_id")
atBatResultsTable.addFk("batter_id", "pro_players", "player_id")
atBatResultsTable.addFk("pitch_id", "pitches", "pitch_id")
atBatResultsTable.addFk("ab_type_id", "ab_types", "ab_type_id")
    ### Table Cols
atBatResultsTable.addCol("play_num", "INT")
atBatResultsTable.addCol("hit_style", "INT", True)
atBatResultsTable.addCol("hit_hardness", "INT", True)
atBatResultsTable.addCol("hit_angle", "INT", True)
atBatResultsTable.addCol("hit_distance", "INT", True)
    ### Table Indexes
atBatResultsTable.addIndex("pitcher_ab", "pitcher_id, game_id")
atBatResultsTable.addIndex("batter_ab", "batter_id, game_id")
###############




### AtBatTypes Table
atBatTypesTable = TB("ab_types")
    ### Primary Key
atBatTypesTable.addPk("ab_type_id", "INT")
    ### Table Cols
atBatTypesTable.addCol("title", "TEXT")
atBatTypesTable.addCol("is_ab", "INT")
atBatTypesTable.addCol("on_base", "INT")
atBatTypesTable.addCol("is_hit", "INT")
atBatTypesTable.addCol("is_out", "INT")
atBatTypesTable.addCol("ex_out", "INT")
atBatTypesTable.addCol("start_base", "INT")
###############


### Lineups Table
lineupsTable = TB("lineups")
    ### Primary Key
lineupsTable.addPk("lineup_id", "INT")
    ### Foreign Keys
lineupsTable.addFk("game_id", "games", "game_id")
lineupsTable.addFk("team_id", "pro_teams", "team_id")
lineupsTable.addFk("opp_id", "pro_teams", "team_id")
lineupsTable.addFk("player_id", "pro_players", "player_id")
    ### Table Cols
lineupsTable.addCol("batt_order", "INT")
lineupsTable.addCol("sub_order", "INT")
lineupsTable.addCol("pos", "TEXT")
###############


### Bullpens Table
bullpensTable = TB("bullpens")
    ### Primary Key
bullpensTable.addPk("bullpen_id", "INT")
    ### Foreign Keys
bullpensTable.addFk("game_id", "games", "game_id")
bullpensTable.addFk("team_id", "pro_teams", "team_id")
bullpensTable.addFk("opp_id", "pro_teams", "team_id")
bullpensTable.addFk("player_id", "pro_players", "player_id")
    ### Table Cols
bullpensTable.addCol("pitch_order", "INT")
###############


### dkYahoo Table
dkYahooTable = TB("dk_yahoo")
    ### Table Cols
dkYahooTable.addCol("dk_id", "TEXT")
dkYahooTable.addCol("yahoo_id", "INT")
dkYahooTable.addCol("team_id", "TEXT")
    ### Primary Key
dkYahooTable.multiPk("yahoo_id, dk_id, team_id")
###############


### dkTeam Table
dkTeamTable = TB("dk_team")
    ### Primary Key
dkTeamTable.addPk("dk_id", "TEXT")
    ### Table Cols
dkTeamTable.addCol("team_id", "INT")
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


### dkSheetPlayers Table
dkSheetPlayersTable = TB("dk_sheet_players")
    ### Primary Key
dkSheetPlayersTable.addPk("dk_sheet_player_id", "INT")
    ### Foreign Keys
dkSheetPlayersTable.addFk("dk_sheet_id", "dk_sheets", "dk_sheet_id")
dkSheetPlayersTable.addFk("dk_price_id", "dk_prices", "dk_price_id")
###############


### dkPrice Table
dkPriceTable = TB("dk_prices")
    ### Primary Key
dkPriceTable.addPk("dk_price_id", "INT")
    ### Foreign Keys
dkPriceTable.addFk("team_id", "dk_team", "dk_id")
dkPriceTable.addFk("opp_id", "dk_team", "dk_id")
    ### Table Cols
dkPriceTable.addCol("game_id", "INT")
dkPriceTable.addCol("dk_id", "INT")
dkPriceTable.addCol("price", "INT")
dkPriceTable.addCol("pos", "TEXT")
    ### Table Indexes
dkPriceTable.addIndex("price_player", "dk_id, game_id")
###############


threeRuns = re.compile("\[\d*?\], \[\d*?\] and \[\d*?\] scored")
twoRuns = re.compile("\[\d*?\] and \[\d*?\] scored")
runScored = re.compile("\[\d*?\] scored")


pitchTypes = ((1,"Fastball"),
                (2,"Curveball"),
                (3,"Slider"),
                (4,"Changeup"),
                (6,"Knuckleball"),
                (7,"Unknown"),
                (8,"Split-Finger"),
                ("9","Cut Fastball"))


pitchResults = ((0,"Ball"),
                (1,"Called Strike"),
                (2,"Swinging Strike"),
                (3,"Foul Ball"),
                (5,"Bunt Foul"),
                (10,"In Play"))


                # title, is_ab, on_base, is_hit, is_out, ex_out, starting_base
atBatResults = (("Ground Out", 1, 0, 0, 1, 1, 0),
                ("Strike Out", 1, 0, 0, 1, 1, 0),
                ("Single", 1, 1, 1, 0, 0, 1),
                ("Fly Out", 1, 0, 0, 1, 1, 0),
                ("Walk", 0, 1, 0, 0, 0, 1),
                ("Line Out", 1, 0, 0, 1, 1, 0),
                ("Double", 1, 1, 1, 0, 0, 2),
                ("Pop Out", 1, 0, 0, 1, 1, 0),
                ("Home Run", 1, 1, 1, 0, 0, 4),
                ("Fielder's Choice", 1, 0, 0, 1, 1, 1),
                ("Double Play", 1, 0, 0, 1, 1, 0),
                ("Fouled Out", 1, 0, 0, 1, 1, 0),
                ("Hit by Pitch", 0, 1, 0, 0, 0, 1),
                ("Reached on Error", 1, 0, 0, 0, 1, 1),
                ("Sacrifice", 0, 0, 0, 1, 1, 0),
                ("Triple", 1, 1, 1, 0, 0, 3),
                ("Reached on Interference", 0, 1, 0, 0, 1, 1),
                ("Triple Play", 1, 0, 0, 1, 1, 0),
                ("Out on Interference", 1, 0, 0, 1, 1, 0),
                ("Out of Order", 1, 0, 0, 1, 1, 0))


statTypes = [{"stat_id": 1, "title": "Plate Appearance", "abrv": "PA"},
                ###########
                {"stat_id": 2, "title": "At Bats", "abrv": "AB"},
                {"stat_id": 3, "title": "Runs", "abrv": "R"},
                {"stat_id": 4, "title": "Hits", "abrv": "H"},
                ##########
                {"stat_id": 5, "title": "Doubles", "abrv": "2B"},
                {"stat_id": 6, "title": "Triples", "abrv": "3B"},
                {"stat_id": 7, "title": "Home Runs", "abrv": "HR"},
                {"stat_id": 8, "title": "Runs Batted In", "abrv": "RBI"},
                ###############
                {"stat_id": 9, "title": "Hit By Pitch", "abrv": "HBP"},
                {"stat_id": 10, "title": "Total Bases", "abrv": "TB"},
                {"stat_id": 12, "title": "Stolen Bases", "abrv": "SB"},
                {"stat_id": 13, "title": "Caught Stealing", "abrv": "CS"},
                ##############
                {"stat_id": 14, "title": "Bases on Balls", "abrv": "BB"},
                {"stat_id": 15, "title": "Singles", "abrv": "1B"},
                {"stat_id": 17, "title": "Strikeouts", "abrv": "SO"},
                {"stat_id": 23, "title": "Batting Average", "abrv": "AVG"},
                {"stat_id": 53, "title": "Left on Base", "abrv": "LOB"},
                {"stat_id": 101, "title": "Wins", "abrv": "W"},
                {"stat_id": 102, "title": "Losses", "abrv": "L"},
                {"stat_id": 107, "title": "Saves", "abrv": "SV"},
                {"stat_id": 111, "title": "Hits", "abrv": "HA"},
                {"stat_id": 113, "title": "Runs", "abrv": "RA"},
                {"stat_id": 114, "title": "Earned Runs", "abrv": "ER"},
                {"stat_id": 115, "title": "Home Runs", "abrv": "HRA"},
                {"stat_id": 118, "title": "Bases on Balls", "abrv": "BBA"},
                {"stat_id": 119, "title": "Hit By Pitch", "abrv": "HBPA"},
                ###############
                {"stat_id": 121, "title": "Strikeouts", "abrv": "K"},
                {"stat_id": 122, "title": "Stolen Bases", "abrv": "SBA"},
                {"stat_id": 123, "title": "Caught Stealing", "abrv": "CSA"},
                ####################
                {"stat_id": 136, "title": "Holds", "abrv": "HLD"},
                {"stat_id": 139, "title": "Innings Pitched", "abrv": "IP"},
                {"stat_id": 140, "title": "Earned Run Average", "abrv": "ERA"},
                {"stat_id": 141, "title": "Walks plus Hits per Inning Pitched", "abrv": "WHIP"},
                {"stat_id": 147, "title": "Blown Saves", "abrv": "BS"},
                {"stat_id": 401, "title": "Batting Avg", "abrv": "AVG"},
                {"stat_id": 402, "title": "Runs", "abrv": "R"},
                {"stat_id": 403, "title": "Hits", "abrv": "H"},
                {"stat_id": 404, "title": "Homeruns", "abrv": "HR"},
                {"stat_id": 405, "title": "Runs Batted In", "abrv": "RBI"},
                {"stat_id": 406, "title": "At Bats", "abrv": "AB"},
                {"stat_id": 409, "title": "Stolen Bases", "abrv": "SB"},
                {"stat_id": 411, "title": "Strikeouts", "abrv": "SO"},
                {"stat_id": 415, "title": "Bases on Balls", "abrv": "BB"},
                {"stat_id": 416, "title": "Total Left on Base", "abrv": "LOB"},
                {"stat_id": 502, "title": "Hits", "abrv": "HA"},
                {"stat_id": 503, "title": "Walks", "abrv": "BBA"},
                {"stat_id": 504, "title": "Strikeouts", "abrv": "K"},
                {"stat_id": 505, "title": "Runs", "abrv": "RA"},
                {"stat_id": 506, "title": "Earned Runs", "abrv": "ER"},
                {"stat_id": 507, "title": "Home Runs", "abrv": "HRA"},
                {"stat_id": 512, "title": "Full Innings Pitched", "abrv": "IP"}]


positions = [{'pos_id': '21', 'abrv': 'SP', 'title': 'Starting Pitcher'},
                {'pos_id': '22', 'abrv': 'RP', 'title': 'Relief Pitcher'},
                {'pos_id': '23', 'abrv': 'CL', 'title': 'Closer'},
                {'pos_id': '0', 'abrv': 'DH', 'title': 'Designated Hitter'},
                {'pos_id': '1', 'abrv': 'P', 'title': 'Pitcher'},
                {'pos_id': '2', 'abrv': 'C', 'title': 'Catcher'},
                {'pos_id': '3', 'abrv': '1B', 'title': 'First Base'},
                {'pos_id': '4', 'abrv': '2B', 'title': 'Second Base'},
                {'pos_id': '5', 'abrv': '3B', 'title': 'Third Base'},
                {'pos_id': '6', 'abrv': 'SS', 'title': 'Shortstop'},
                {'pos_id': '7', 'abrv': 'LF', 'title': 'Left Field'},
                {'pos_id': '8', 'abrv': 'CF', 'title': 'Center Field'},
                {'pos_id': '9', 'abrv': 'RF', 'title': 'Right Field'}]


teams = [{'abrv': 'TB', 'team_id': '30', 'conference': 'American League', 'division': 'East', 'primary_color': '092c5c', 'secondary_color': '8fbce6', 'first_name': 'Tampa Bay', 'last_name': 'Rays'},
            {'abrv': 'WAS', 'team_id': '20', 'conference': 'National League', 'division': 'East', 'primary_color': '14225a', 'secondary_color': '14225a', 'first_name': 'Washington', 'last_name': 'Nationals'},
            {'abrv': 'NYY', 'team_id': '10', 'conference': 'American League', 'division': 'East', 'primary_color': '003087', 'secondary_color': 'e4002c', 'first_name': 'New York', 'last_name': 'Yankees'},
            {'abrv': 'NYM', 'team_id': '21', 'conference': 'National League', 'division': 'East', 'primary_color': '002d72', 'secondary_color': 'ff5910', 'first_name': 'New York', 'last_name': 'Mets'},
            {'abrv': 'OAK', 'team_id': '11', 'conference': 'American League', 'division': 'West', 'primary_color': '003831', 'secondary_color': 'efb21e', 'first_name': 'Oakland', 'last_name': 'Athletics'},
            {'abrv': 'PHI', 'team_id': '22', 'conference': 'National League', 'division': 'East', 'primary_color': 'e81828', 'secondary_color': '002d72', 'first_name': 'Philadelphia', 'last_name': 'Phillies'},
            {'abrv': 'SEA', 'team_id': '12', 'conference': 'American League', 'division': 'West', 'primary_color': '0c2c56', 'secondary_color': '005c5c', 'first_name': 'Seattle', 'last_name': 'Mariners'},
            {'abrv': 'PIT', 'team_id': '23', 'conference': 'National League', 'division': 'Central', 'primary_color': '27251f', 'secondary_color': 'fdb827', 'first_name': 'Pittsburgh', 'last_name': 'Pirates'},
            {'abrv': 'TEX', 'team_id': '13', 'conference': 'American League', 'division': 'West', 'primary_color': '003278', 'secondary_color': 'c0111f', 'first_name': 'Texas', 'last_name': 'Rangers'},
            {'abrv': 'STL', 'team_id': '24', 'conference': 'National League', 'division': 'Central', 'primary_color': 'c41e3a', 'secondary_color': '0c2340', 'first_name': 'St. Louis', 'last_name': 'Cardinals'},
            {'abrv': 'TOR', 'team_id': '14', 'conference': 'American League', 'division': 'East', 'primary_color': '134a8e', 'secondary_color': '1d2d5c', 'first_name': 'Toronto', 'last_name': 'Blue Jays'},
            {'abrv': 'SD', 'team_id': '25', 'conference': 'National League', 'division': 'West', 'primary_color': 'ffc72c', 'secondary_color': '2f241d', 'first_name': 'San Diego', 'last_name': 'Padres'},
            {'abrv': 'ATL', 'team_id': '15', 'conference': 'National League', 'division': 'East', 'primary_color': 'ce1141', 'secondary_color': '13274f', 'first_name': 'Atlanta', 'last_name': 'Braves'},
            {'abrv': 'SF', 'team_id': '26', 'conference': 'National League', 'division': 'West', 'primary_color': 'fd5a1e', 'secondary_color': '27251f', 'first_name': 'San Francisco', 'last_name': 'Giants'},
            {'abrv': 'CHC', 'team_id': '16', 'conference': 'National League', 'division': 'Central', 'primary_color': '0e3386', 'secondary_color': 'cc3433', 'first_name': 'Chicago', 'last_name': 'Cubs'},
            {'abrv': 'COL', 'team_id': '27', 'conference': 'National League', 'division': 'West', 'primary_color': '33006f', 'secondary_color': 'c4ced4', 'first_name': 'Colorado', 'last_name': 'Rockies'},
            {'abrv': 'CIN', 'team_id': '17', 'conference': 'National League', 'division': 'Central', 'primary_color': 'c6011f', 'secondary_color': '000000', 'first_name': 'Cincinnati', 'last_name': 'Reds'},
            {'abrv': 'MIA', 'team_id': '28', 'conference': 'National League', 'division': 'East', 'primary_color': '00a3e0', 'secondary_color': 'ef3340', 'first_name': 'Miami', 'last_name': 'Marlins'},
            {'abrv': 'HOU', 'team_id': '18', 'conference': 'American League', 'division': 'West', 'primary_color': '002d62', 'secondary_color': 'eb6e1f', 'first_name': 'Houston', 'last_name': 'Astros'},
            {'abrv': 'ARI', 'team_id': '29', 'conference': 'National League', 'division': 'West', 'primary_color': 'a71930', 'secondary_color': 'e3d4ad', 'first_name': 'Arizona', 'last_name': 'Diamondbacks'},
            {'abrv': 'BAL', 'team_id': '1', 'conference': 'American League', 'division': 'East', 'primary_color': 'df4601', 'secondary_color': '000000', 'first_name': 'Baltimore', 'last_name': 'Orioles'},
            {'abrv': 'LAD', 'team_id': '19', 'conference': 'National League', 'division': 'West', 'primary_color': '005a9c', 'secondary_color': 'a5acaf', 'first_name': 'Los Angeles', 'last_name': 'Dodgers'},
            {'abrv': 'BOS', 'team_id': '2', 'conference': 'American League', 'division': 'East', 'primary_color': 'bd3039', 'secondary_color': '0c2340', 'first_name': 'Boston', 'last_name': 'Red Sox'},
            {'abrv': 'LAA', 'team_id': '3', 'conference': 'American League', 'division': 'West', 'primary_color': '003263', 'secondary_color': 'ba0021', 'first_name': 'Los Angeles', 'last_name': 'Angels'},
            {'abrv': 'CWS', 'team_id': '4', 'conference': 'American League', 'division': 'Central', 'primary_color': '27251f', 'secondary_color': 'c4ced4', 'first_name': 'Chicago', 'last_name': 'White Sox'},
            {'abrv': 'CLE', 'team_id': '5', 'conference': 'American League', 'division': 'Central', 'primary_color': '0c2340', 'secondary_color': 'e31937', 'first_name': 'Cleveland', 'last_name': 'Indians'},
            {'abrv': 'DET', 'team_id': '6', 'conference': 'American League', 'division': 'Central', 'primary_color': '0c2340', 'secondary_color': 'fa4616', 'first_name': 'Detroit', 'last_name': 'Tigers'},
            {'abrv': 'KC', 'team_id': '7', 'conference': 'American League', 'division': 'Central', 'primary_color': '004687', 'secondary_color': 'bd9b60', 'first_name': 'Kansas City', 'last_name': 'Royals'},
            {'abrv': 'MIL', 'team_id': '8', 'conference': 'National League', 'division': 'Central', 'primary_color': '0a2351', 'secondary_color': 'b6922e', 'first_name': 'Milwaukee', 'last_name': 'Brewers'},
            {'abrv': 'MIN', 'team_id': '9', 'conference': 'American League', 'division': 'Central', 'primary_color': '002b5c', 'secondary_color': 'd31145', 'first_name': 'Minnesota', 'last_name': 'Twins'}]


runnerResults = ("Stolen Base", "Wild Pitch", "Caught Stealing", "Passed Ball",
                    "Fielder's Indifference", "Picked Off", "Advanced on Error",
                    "Balk")


managerResults = ("Pitching Change", "Fielding Change", "Pinch Hitter", "Pinch Runner")


positionNumbers = {"pitcher":1, "catcher":2, "first":3, "second":4, "third":5,
                    "shortstop":6, "left":7, "center":8, "right":9}


valuesBase = (0,1667,3333, 5000, 6667, 8333, 10000, 11667, 13333, 15000, 16667)
values = list(valuesBase) + [ x*-1 for x in valuesBase if x ]
pitchLocations = []
for horizontal in values:
    for vertical in values:
        # append a tuple (valA, valB)
        pitchLocations.append((horizontal,vertical))


def sortingHat(horizontal, vertical):
    # find a box for the pitch location
    y = round(vertical/1667) - 11
    x = round(horizontal/1667) + 11

    yValue = _hat(abs(y))
    xValue = _hat(x)+1
    return (yValue *5) + xValue


def _hat(item):
    value = None
    if item <= 3:
        value = 0
    elif item <= 7:
        value = 1
    elif item <=12:
        value = 2
    elif item <= 16:
        value = 3
    else:
        value = 4
    return value


unearnId = -20
emptyId = -10
noRbiId = -5




createTableCmd = """
                    CREATE TABLE IF NOT EXISTS {0[tableName]} (
                        player_id INT NOT NULL,
                        history_id TEXT NOT NULL,
                        {0[pitch_contact]}
                        {0[classifierCmd]}
                        intercept REAL NOT NULL,
                        {0[tableCmd]}
                        PRIMARY KEY ( {0[pkCmd]} ),
                        FOREIGN KEY (player_id) REFERENCES pro_players (player_id) )
                """


pitchesCmd =  """
                SELECT {0[selectCmd]}
                FROM pitches AS pitch0
                INNER JOIN pro_players AS pitcher ON pitch0.pitcher_id = pitcher.player_id
                INNER JOIN pro_players AS batter ON pitch0.batter_id = batter.player_id
                INNER JOIN pitch_locations ON pitch0.location_id = pitch_locations.location_id
                INNER JOIN lineups ON pitch0.game_id = lineups.game_id AND pitch0.batter_id = lineups.player_id

                INNER JOIN (SELECT pitch_id, pitch_type_id AS pitch_type_1, box AS box_1, prev_pitch_id
                                    FROM pitches
                                    INNER JOIN pitch_locations
                                        ON pitches.location_id = pitch_locations.location_id
                                    ) AS pitch1
                    ON pitch0.prev_pitch_id = pitch1.pitch_id

                INNER JOIN (SELECT pitch_id, pitch_type_id AS pitch_type_2, box AS box_2, prev_pitch_id
                                    FROM pitches
                                    INNER JOIN pitch_locations
                                        ON pitches.location_id = pitch_locations.location_id
                                    ) AS pitch2
                    ON pitch1.prev_pitch_id = pitch2.pitch_id

                WHERE pitcher_id = ?
                """


pitchContactCmd = """
                    SELECT {0[selectCmd]}
                    FROM pitches
                    LEFT OUTER JOIN contacts ON contacts.pitch_id = pitches.pitch_id
                    INNER JOIN pro_players AS pitcher ON pitches.pitcher_id = pitcher.player_id
                    INNER JOIN pro_players AS batter ON pitches.batter_id = batter.player_id
                    INNER JOIN pitch_locations ON pitches.location_id = pitch_locations.location_id

                    WHERE pitcher_id = ?
                    """


pitchRemoveCmd = """
                    SELECT {0[selectCmd]}
                    FROM removals

                    WHERE pitcher_id = ?
                    """


pitchReplaceCmd = """
                    SELECT {0[selectCmd]}
                    FROM new_pitchers

                    WHERE team_id = ?
                    """


pitchAtBatsCmd = """
                SELECT ab_results.game_id,
                        ab_results.play_num,
                        pitch_num,
                        runs
                FROM ab_results
                INNER JOIN pitches ON ab_results.pitch_id = pitches.pitch_id
                WHERE pitcher_id = ?
                """








battPitchesCmd = """
                    SELECT {0[selectCmd]}
                    FROM pitches
                    LEFT OUTER JOIN contacts ON contacts.pitch_id = pitches.pitch_id
                    INNER JOIN pro_players AS pitcher ON pitches.pitcher_id = pitcher.player_id
                    INNER JOIN pro_players AS batter ON pitches.batter_id = batter.player_id
                    INNER JOIN pitch_locations ON pitches.location_id = pitch_locations.location_id

                    WHERE batter_id = ?
                    """


battContactsCmd = """
                    SELECT {0[selectCmd]}
                    FROM contacts
                    INNER JOIN pitches ON contacts.pitch_id = pitches.pitch_id
                    INNER JOIN pro_players AS pitcher ON pitches.pitcher_id = pitcher.player_id
                    INNER JOIN pro_players AS batter ON pitches.batter_id = batter.player_id
                    INNER JOIN pitch_locations ON pitches.location_id = pitch_locations.location_id

                    WHERE batter_id = ?
                    """


################################################################################
################################################################################


class MLBDB(DB):

    dbPath = os.environ["HOME"]+"/Yahoo/mlb/mlb.db"

    def __init__(self):
        super().__init__(self.dbPath)

    def getTableList(self):
        return (gamesTable, proPlayersTable, proTeamsTable, stadiumsTable, lineupsTable,
                batterStatsTable, pitcherStatsTable, teamStatsTable,
                statTypesTable, pitchTypesTable, pitchResultsTable, pitchLocationsTable,
                pitchesTable, atBatTypesTable, atBatResultsTable, bullpensTable)




    def seed(self):

        for team in teams:
            self.insert(proTeamsTable, info=team)

        for stat in statTypes:
            self.insert(statTypesTable, info=stat)

        self.insert(pitchLocationsTable, values=(-1, -1, -1, -1, False))
        for i, location in enumerate(pitchLocations):
            self.insert(pitchLocationsTable, values=(i, *location, sortingHat(*location), str(False if abs(location[0]) > 10000 or abs(location[1]) > 10000 else True)))

        for values in pitchTypes:
            self.insert(pitchTypesTable, values=values)

        for values in pitchResults:
            self.insert(pitchResultsTable, values=values)

        for i, values in enumerate(atBatResults):
            self.insert(atBatTypesTable, values=(i, *values))


        self.commit()
