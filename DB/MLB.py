import os
import sqlite3
import re
import datetime
import unicodedata

from itertools import chain

from .Database import Database as DB
from .Database import Table as TB
import MLBProjections.MLBProjections.Environ as ENV
from MLBProjections.MLBProjections.Utils.UpdateMixIn import UpdateMixIn
import MLBProjections.MLBProjections.Utils.ResultParse as RP

# for debugging
from pprint import pprint

################################################################################
################################################################################

def normal(name):
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    return name

### Meta Table
metaTable = TB.Table("game_meta")
    ### Primary Key
metaTable.addPk("game_id", "INT")
    ## Foreign Keys
metaTable.addFk("home_id", "pro_teams", "team_id")
metaTable.addFk("away_id", "pro_teams", "team_id")
metaTable.addFk("stadium_id", "stadiums", "stadium_id")
###############


### Games Table
gamesTable = TB.Table("games")
    ### Primary Key
gamesTable.addPk("game_id", "INT")
    ## Foreign Keys
gamesTable.addFk("home_id", "pro_teams", "team_id")
gamesTable.addFk("away_id", "pro_teams", "team_id")
gamesTable.addFk("winner_id", "pro_teams", "team_id")
gamesTable.addFk("loser_id", "pro_teams", "team_id")
gamesTable.addFk("stadium_id", "stadiums", "stadium_id")
    ## Table Cols
gamesTable.addCol("season", "INT")
gamesTable.addCol("game_date", "REAL")
gamesTable.addCol("season_type", "TEXT")
    ## Table Indexes
gamesTable.addIndex("season_date", "season, game_date")
###############



### ProPlayers Table
proPlayersTable = TB.Table("pro_players")
    ### Primary Key
proPlayersTable.addPk("player_id", "INT")
    ## Table Cols
proPlayersTable.addCol("first_name", "TEXT")
proPlayersTable.addCol("last_name", "TEXT")
proPlayersTable.addCol("pos", "INT")
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
proTeamsTable = TB.Table("pro_teams")
    ### Primary Key
proTeamsTable.addPk("team_id", "INT")
    ### Foreign Key
proTeamsTable.addFk("stadium_id", "stadiums", "stadium_id")
    ## Table Cols
proTeamsTable.addCol("abrv", "TEXT")
proTeamsTable.addCol("city", "TEXT")
proTeamsTable.addCol("mascot", "TEXT")
proTeamsTable.addCol("league", "TEXT")
proTeamsTable.addCol("division", "TEXT")
proTeamsTable.addCol("color", "TEXT")
###############


### Stadiums Table
stadiumsTable = TB.Table("stadiums")
    ### Primary Key
stadiumsTable.addPk("stadium_id", "INT")
    ## Table Cols
stadiumsTable.addCol("title", "TEXT")
###############


### PlayerStats Table
playerStatsTable = TB.Table("player_stats")
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
playerStatsTable.addIndex("player_game_stats", "player_id, stat_id")
###############


### TeamStats Table
teamStatsTable = TB.Table("team_stats")
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
statTypesTable = TB.Table("stat_types")
    ### Primary Key
statTypesTable.addPk("stat_id", "INT")
    ## Table Cols
statTypesTable.addCol("title", "TEXT")
statTypesTable.addCol("abrv", "TEXT")
###############



### PitchTypes Table
pitchTypesTable = TB.Table("pitch_types")
    ### Primary Key
pitchTypesTable.addPk("pitch_type_id", "INT")
    ## Table Cols
pitchTypesTable.addCol("title", "TEXT")
###############


### PitchResults Table
pitchResultsTable = TB.Table("pitch_results")
    ### Primary Key
pitchResultsTable.addPk("pitch_result_id", "INT")
    ## Table Cols
pitchResultsTable.addCol("title", "TEXT")
###############


### PitchLocations Table
pitchLocationsTable = TB.Table("pitch_locations")
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
pitchesTable = TB.Table("pitches")
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
atBatResultsTable = TB.Table("ab_results")
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
atBatTypesTable = TB.Table("ab_types")
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
lineupsTable = TB.Table("lineups")
    ### Primary Key
lineupsTable.addPk("lineup_id", "INT")
    ### Foreign Keys
lineupsTable.addFk("game_id", "games", "game_id")
lineupsTable.addFk("team_id", "pro_teams", "team_id")
lineupsTable.addFk("player_id", "pro_players", "player_id")
    ### Table Cols
lineupsTable.addCol("batt_order", "INT")
lineupsTable.addCol("sub_order", "INT")
lineupsTable.addCol("pos", "TEXT")
###############


### Bullpens Table
bullpensTable = TB.Table("bullpens")
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
dkYahooTable = TB.Table("dk_yahoo")
    ### Table Cols
dkYahooTable.addCol("dk_id", "TEXT")
dkYahooTable.addCol("yahoo_id", "INT")
dkYahooTable.addCol("team_id", "TEXT")
    ### Primary Key
dkYahooTable.multiPk("yahoo_id, dk_id, team_id")
###############


### dkTeam Table
dkTeamTable = TB.Table("dk_team")
    ### Primary Key
dkTeamTable.addPk("dk_id", "TEXT")
    ### Table Cols
dkTeamTable.addCol("team_id", "INT")
###############


### dkSheet Table
dkSheetTable = TB.Table("dk_sheets")
    ### Primary Key
dkSheetTable.addPk("dk_sheet_id", "INT")
    ### Table Cols
dkSheetTable.addCol("game_type", "TEXT")
dkSheetTable.addCol("start_time", "REAL")
dkSheetTable.addCol("num_games", "INT")
dkSheetTable.addCol("game_date", "TEXT")
###############


### dkSheetGames Table
dkSheetGamesTable = TB.Table("dk_sheet_games")
    ### Primary Key
dkSheetGamesTable.addPk("dk_sheet_game_id", "INT")
    ### Foreign Keys
dkSheetGamesTable.addFk("dk_sheet_id", "dk_sheets", "dk_sheet_id")
    ### Table Cols
dkSheetGamesTable.addCol("game_id", "INT")
###############


### dkSheetPlayers Table
dkSheetPlayersTable = TB.Table("dk_sheet_players")
    ### Primary Key
dkSheetPlayersTable.addPk("dk_sheet_player_id", "INT")
    ### Foreign Keys
dkSheetPlayersTable.addFk("dk_sheet_id", "dk_sheets", "dk_sheet_id")
dkSheetPlayersTable.addFk("dk_price_id", "dk_prices", "dk_price_id")
###############


### dkPrice Table
dkPriceTable = TB.Table("dk_prices")
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


class MLBDatabase(DB.Database, UpdateMixIn):

    def __init__(self):
        UpdateMixIn.__init__(self)
        DB.Database.__init__(self, ENV.getPath("database", fileName="mlb"))


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
        return (gamesTable, proPlayersTable, proTeamsTable, stadiumsTable, lineupsTable,
                playerStatsTable, teamStatsTable, statTypesTable, pitchTypesTable,
                pitchResultsTable, pitchLocationsTable, pitchesTable, atBatTypesTable,
                atBatResultsTable, bullpensTable)


    def enterFileItems(self, itemType, itemTable):
        itemPath = ENV.getPath(itemType).strip("None.json")
        for itemFile in [itemPath+fileName for fileName in os.listdir(itemPath) if os.path.isfile(itemPath+fileName)]:
            info = ENV.getJsonInfo(itemFile)
            self.insert(itemTable, info=info)


    def insertDates(self, checkDate):
        for filePath in ENV.yearMonthDay(checkDate):
            info = ENV.getJsonInfo(filePath+"scoreboard.json")
            for gamePath in ["{}.json".format(filePath+game["game_id"]) for game in info["games"] if game["status"] == "final"]:
                try:
                    self.insertGame(gamePath)
                except sqlite3.IntegrityError as e:
                    print(e)


    def insertGame(self, gamePath):

        pitchTemp = {"HBP":0, "SB":0, "CS":0}
        battTemp = {"PA":0,"HBP":0,"BB":0,"1B":0,"2B":0,"3B":0,"HR":0,"CS":0}
        batters = {}
        pitchers = {}
        batActions = [x[0] for x in atBatResults]

        print("Inserting {}".format(gamePath))

        gameInfo = ENV.getJsonInfo(gamePath)

        gameId = gameInfo["game_id"]
        homeId = gameInfo["home_id"]
        awayId = gameInfo["away_id"]

        if gameInfo.get("season_type", None):
            gameInfo["season_type"] = "reg"

        playerList = [(player["player_id"], player) for player in gameInfo["players"]]
        players = dict(zip([p[0] for p in playerList], [p[1] for p in playerList]))

        # Games Table
        self.insert(gamesTable, info=gameInfo)

        # Lineups Table
        for side in ("home", "away"):
            for lineup in gameInfo["lineups"][side]["B"]:
                lineupId = self.nextKey(lineupsTable)
                lineup["lineup_id"] = lineupId
                lineup["game_id"] = gameId
                lineup["batt_order"] = lineup["order"]
                lineup["team_id"] = gameInfo["{}_id".format(side)]
                lineup["pos"] = lineup["position"][0]
                self.insert(lineupsTable, info=lineup)

            for lineup in gameInfo["lineups"][side]["P"]:
                bullpenId = self.nextKey(bullpensTable)
                lineup["bullpen_id"] = bullpenId
                lineup["game_id"] = gameId
                lineup["pitch_order"] = lineup["order"]
                lineup["team_id"] = gameInfo["{}_id".format(side)]
                oppSide = "away" if side == "home" else "home"
                lineup["opp_id"] = gameInfo["{}_id".format(oppSide)]
                self.insert(bullpensTable, info=lineup)


        for key, values in gameInfo["playerStats"].items():
            playerId = key.split(".")[-1]
            try:
                teamId = players[playerId]["team_id"]
                oppId = homeId if teamId == awayId else awayId
            except KeyError:
                teamId = -1
                oppId = -1
            playerStats = {}

            for group in values:
                for statId, stat in group.items():
                    statId = statId.split(".")[-1]
                    playerStats[statId] = stat

            for key, value in playerStats.items():
                playerStatId = self.nextKey(playerStatsTable)
                if int(key) not in (101, 102, 107):
                    if int(key) == 139:
                        inn,out = str(value).split(".")
                        out = int(out)*3334
                        value = float("{}.{}".format(inn,out))
                    self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, key, value])

        for key, value in gameInfo.get("homeTeamStats", [{},])[0].items():
            oppId = awayId
            teamId = homeId
            value = value
            statId = key.split(".")[-1]

            teamStatId = self.nextKey(teamStatsTable)
            self.insert(teamStatsTable, values=[teamStatId, gameId, teamId, oppId, statId, value])

        for key, value in gameInfo.get("awayTeamStats", [{},])[0].items():
            oppId = homeId
            teamId = awayId
            value = value
            statId = key.split(".")[-1]

            teamStatId = self.nextKey(teamStatsTable)
            self.insert(teamStatsTable, values=[teamStatId, gameId, teamId, oppId, statId, value])


        pbp = gameInfo.get("play_by_play",{}).values()
        pitches = gameInfo.get("pitches",{}).values()

        for play in sorted(chain(pbp, pitches), key=lambda x: int(x["play_num"])):

            info = {
                        "game_id": gameId,
                        "batter_id": play.get("batter",None),
                        "pitcher_id": play.get("pitcher",None),
                        "hit_angle": play.get("hit_angle",None),
                        "hit_distance": play.get("hit_distance",None),
                        "hit_hardness": play.get("hit_hardness",None),
                        "hit_style": play.get("hit_style",None),
                        "pitch_type_id": play.get("pitch_type", 7),
                        "pitch_velocity": play.get("velocity", -1),
                        "sequence": play.get("sequence",None),
                        "play_num": play.get("play_num",None),
                        "pitch_num": play.get("pitch_num",None),
                        "balls": play.get("balls",None),
                        "strikes": play.get("strikes",None),
                        "pitch_result_id": play.get("result",None),
                        "xValue": play.get("horizontal", None),
                        "yValue": play.get("vertical", None)
                    }
            if int(play.get("balls", 0)) > 3:
                info["balls"] = 3
            if int(play.get("strikes", 0)) > 2:
                info["strikes"] = 2




            if play["play_type"] == "PITCH":
                pitcherId = info["pitcher_id"]
                batterId = info["batter_id"]


                # Table column entries
                pitchId = self.nextKey(pitchesTable)
                try:
                    locationId = self.getKey(pitchLocationsTable, x_value=info["xValue"], y_value =info["yValue"])
                except sqlite3.OperationalError:
                    locationId = -1
                # Entering column values into info dictionary
                for key, value in (("pitch_id", pitchId), ("pitch_location_id", locationId)):
                    info[key] = value

                self.insert(pitchesTable, info=info)


            if play["play_type"] == "RESULT":
                action, _, _ = RP.parseAtBat(play["text"])
                for i, abResult in enumerate(atBatResults):
                    if abResult[0] == action:
                        # print(action)
                        info["ab_result_id"] = self.nextKey(atBatResultsTable)
                        info["ab_type_id"] = i
                        info["pitch_id"] = pitchId

                        self.insert(atBatResultsTable, info=info)

                if action in batActions:
                    batterId = play["batter"]
                    pitcherId = play["pitcher"]

                    batterStats = batters.get(batterId, battTemp.copy())
                    pitcherStats = pitchers.get(pitcherId, pitchTemp.copy())

                    batterStats["PA"] += 1
                    if action in ("Single", "Double", "Triple", "Home Run"):
                        if action == "Single":
                            batterStats["1B"] += 1
                        if action == "Double":
                            batterStats["2B"] += 1
                        if action == "Triple":
                            batterStats["3B"] += 1
                        if action == "Home Run":
                            batterStats["HR"] += 1

                    if action == "Hit by Pitch":
                        pitcherStats["HBP"] += 1
                        batterStats["HBP"] += 1

                    batters[batterId] = batterStats
                    pitchers[pitcherId] = pitcherStats

        for playerId, values in batters.items():
            try:
                teamId = players[playerId]["team_id"]
                oppId = homeId if teamId == awayId else awayId
            except KeyError:
                teamId = -1
                oppId = -1

            # PA
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 1, values["PA"]])
            # Singles
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 15, values["1B"]])
            # Doubles
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 5, values["2B"]])
            # Triples
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 6, values["3B"]])
            # HBP
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 9, values["HBP"]])
            # Total Bases
            playerStatId = self.nextKey(playerStatsTable)
            totalBases = int(values["1B"]) + (int(values["2B"])*2) +(int(values["3B"])*3) + (int(values["HR"])*4)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 10, totalBases])
            # Caught Stealing
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 13, values["CS"]])

        for playerId, values in pitchers.items():
            try:
                teamId = players[playerId]["team_id"]
                oppId = homeId if teamId == awayId else awayId
            except KeyError:
                teamId = -1
                oppId = -1

            # HBP
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 119, values["HBP"]])
            # Stolen Bases
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 122, values["SB"]])
            # Caught Stealing
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 123, values["CS"]])

            # W
            result =  int(playerId) == int(gameInfo["byline"]["winning_pitcher"].split(".")[-1])
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 101, result])
            # L
            result = int(playerId) == int(gameInfo["byline"]["losing_pitcher"].split(".")[-1])
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 102, result])
            # SV
            result = int(playerId) == int(gameInfo["byline"].get("saving_pitcher", "-11").split(".")[-1])
            playerStatId = self.nextKey(playerStatsTable)
            self.insert(playerStatsTable, values=[playerStatId, gameId, playerId, teamId, oppId, 107, result])





        for play in gameInfo["play_by_play"].values():
            if play["play_type"] == "RUNNER":
                action = RP.parseRunner(play["text"])
                if action in ("Stolen Base", "Caught Stealing"):
                    index = str(int(play["play_num"]) -1)
                    runnerId = play["players"]
                    try:
                        pitcherId = gameInfo["pitches"][index]["pitcher"]
                    except KeyError:
                        pitcherId = -1
                    batterStats = batters.get(runnerId, battTemp.copy())
                    pitcherStats = pitchers.get(pitcherId, pitchTemp.copy())

                    if action == "Stolen Base":
                        pitcherStats["SB"] += 1
                    else:
                        pitcherStats["CS"] += 1
                        batterStats["CS"] += 1

                    batters[runnerId] = batterStats
                    pitchers[pitcherId] = pitcherStats










    def seed(self):

        self.clearManagerFile()

        itemPath = ENV.getPath("player").strip("None.json")
        for itemFile in [itemPath+fileName for fileName in os.listdir(itemPath) if os.path.isfile(itemPath+fileName)]:
            info = ENV.getJsonInfo(itemFile)
            info["first_name"] = normal(info["first_name"])
            info["last_name"] = normal(info["last_name"])
            self.insert(proPlayersTable, info=info)

        self.enterFileItems("team", proTeamsTable)
        self.enterFileItems("stadium", stadiumsTable)

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



################################################################################
################################################################################


class MLBDFS(DB.Database):

    def __init__(self):
        super().__init__(ENV.getPath("dfs"))


    def getTableList(self):
        return (dkYahooTable, dkTeamTable, dkPriceTable, dkSheetTable,
                dkSheetGamesTable, dkSheetPlayersTable)


    def seed(self):
        pass


################################################################################
################################################################################
