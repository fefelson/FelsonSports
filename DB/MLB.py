import os
import re
import datetime


from ..Models import DatabaseManager as DB, yId, normal
from ..Utils import ResultsParse as RP
from itertools import chain
from sqlite3 import IntegrityError, OperationalError
# for debugging
from pprint import pprint

################################################################################
################################################################################






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


teams = [{'abrv': 'TB',
  'conference': 'American League',
  'division': 'East',
  'first_name': 'Tampa Bay',
  'last_name': 'Rays',
  'primary_color': '092c5c',
  'secondary_color': '8fbce6',
  'team_id': '30',
  'yahoo_slug': 'tampa-bay'},
 {'abrv': 'WAS',
  'conference': 'National League',
  'division': 'East',
  'first_name': 'Washington',
  'last_name': 'Nationals',
  'primary_color': '14225a',
  'secondary_color': '14225a',
  'team_id': '20',
  'yahoo_slug': 'washington'},
 {'abrv': 'NYY',
  'conference': 'American League',
  'division': 'East',
  'first_name': 'New York',
  'last_name': 'Yankees',
  'primary_color': '003087',
  'secondary_color': 'e4002c',
  'team_id': '10',
  'yahoo_slug': 'ny-yankees'},
 {'abrv': 'NYM',
  'conference': 'National League',
  'division': 'East',
  'first_name': 'New York',
  'last_name': 'Mets',
  'primary_color': '002d72',
  'secondary_color': 'ff5910',
  'team_id': '21',
  'yahoo_slug': 'ny-mets'},
 {'abrv': 'OAK',
  'conference': 'American League',
  'division': 'West',
  'first_name': 'Oakland',
  'last_name': 'Athletics',
  'primary_color': '003831',
  'secondary_color': 'efb21e',
  'team_id': '11',
  'yahoo_slug': 'oakland'},
 {'abrv': 'PHI',
  'conference': 'National League',
  'division': 'East',
  'first_name': 'Philadelphia',
  'last_name': 'Phillies',
  'primary_color': 'e81828',
  'secondary_color': '002d72',
  'team_id': '22',
  'yahoo_slug': 'philadelphia'},
 {'abrv': 'SEA',
  'conference': 'American League',
  'division': 'West',
  'first_name': 'Seattle',
  'last_name': 'Mariners',
  'primary_color': '0c2c56',
  'secondary_color': '005c5c',
  'team_id': '12',
  'yahoo_slug': 'seattle'},
 {'abrv': 'PIT',
  'conference': 'National League',
  'division': 'Central',
  'first_name': 'Pittsburgh',
  'last_name': 'Pirates',
  'primary_color': '27251f',
  'secondary_color': 'fdb827',
  'team_id': '23',
  'yahoo_slug': 'pittsburgh'},
 {'abrv': 'TEX',
  'conference': 'American League',
  'division': 'West',
  'first_name': 'Texas',
  'last_name': 'Rangers',
  'primary_color': '003278',
  'secondary_color': 'c0111f',
  'team_id': '13',
  'yahoo_slug': 'texas'},
 {'abrv': 'STL',
  'conference': 'National League',
  'division': 'Central',
  'first_name': 'St. Louis',
  'last_name': 'Cardinals',
  'primary_color': 'c41e3a',
  'secondary_color': '0c2340',
  'team_id': '24',
  'yahoo_slug': 'st-louis'},
 {'abrv': 'TOR',
  'conference': 'American League',
  'division': 'East',
  'first_name': 'Toronto',
  'last_name': 'Blue Jays',
  'primary_color': '134a8e',
  'secondary_color': '1d2d5c',
  'team_id': '14',
  'yahoo_slug': 'toronto'},
 {'abrv': 'SD',
  'conference': 'National League',
  'division': 'West',
  'first_name': 'San Diego',
  'last_name': 'Padres',
  'primary_color': 'ffc72c',
  'secondary_color': '2f241d',
  'team_id': '25',
  'yahoo_slug': 'san-diego'},
 {'abrv': 'ATL',
  'conference': 'National League',
  'division': 'East',
  'first_name': 'Atlanta',
  'last_name': 'Braves',
  'primary_color': 'ce1141',
  'secondary_color': '13274f',
  'team_id': '15',
  'yahoo_slug': 'atlanta'},
 {'abrv': 'SF',
  'conference': 'National League',
  'division': 'West',
  'first_name': 'San Francisco',
  'last_name': 'Giants',
  'primary_color': 'fd5a1e',
  'secondary_color': '27251f',
  'team_id': '26',
  'yahoo_slug': 'san-francisco'},
 {'abrv': 'CHC',
  'conference': 'National League',
  'division': 'Central',
  'first_name': 'Chicago',
  'last_name': 'Cubs',
  'primary_color': '0e3386',
  'secondary_color': 'cc3433',
  'team_id': '16',
  'yahoo_slug': 'chi-cubs'},
 {'abrv': 'COL',
  'conference': 'National League',
  'division': 'West',
  'first_name': 'Colorado',
  'last_name': 'Rockies',
  'primary_color': '33006f',
  'secondary_color': 'c4ced4',
  'team_id': '27',
  'yahoo_slug': 'colorado'},
 {'abrv': 'CIN',
  'conference': 'National League',
  'division': 'Central',
  'first_name': 'Cincinnati',
  'last_name': 'Reds',
  'primary_color': 'c6011f',
  'secondary_color': '000000',
  'team_id': '17',
  'yahoo_slug': 'cincinnati'},
 {'abrv': 'MIA',
  'conference': 'National League',
  'division': 'East',
  'first_name': 'Miami',
  'last_name': 'Marlins',
  'primary_color': '00a3e0',
  'secondary_color': 'ef3340',
  'team_id': '28',
  'yahoo_slug': 'miami'},
 {'abrv': 'HOU',
  'conference': 'American League',
  'division': 'West',
  'first_name': 'Houston',
  'last_name': 'Astros',
  'primary_color': '002d62',
  'secondary_color': 'eb6e1f',
  'team_id': '18',
  'yahoo_slug': 'houston'},
 {'abrv': 'ARI',
  'conference': 'National League',
  'division': 'West',
  'first_name': 'Arizona',
  'last_name': 'Diamondbacks',
  'primary_color': 'a71930',
  'secondary_color': 'e3d4ad',
  'team_id': '29',
  'yahoo_slug': 'arizona'},
 {'abrv': 'BAL',
  'conference': 'American League',
  'division': 'East',
  'first_name': 'Baltimore',
  'last_name': 'Orioles',
  'primary_color': 'df4601',
  'secondary_color': '000000',
  'team_id': '1',
  'yahoo_slug': 'baltimore'},
 {'abrv': 'LAD',
  'conference': 'National League',
  'division': 'West',
  'first_name': 'Los Angeles',
  'last_name': 'Dodgers',
  'primary_color': '005a9c',
  'secondary_color': 'a5acaf',
  'team_id': '19',
  'yahoo_slug': 'la-dodgers'},
 {'abrv': 'BOS',
  'conference': 'American League',
  'division': 'East',
  'first_name': 'Boston',
  'last_name': 'Red Sox',
  'primary_color': 'bd3039',
  'secondary_color': '0c2340',
  'team_id': '2',
  'yahoo_slug': 'boston'},
 {'abrv': 'LAA',
  'conference': 'American League',
  'division': 'West',
  'first_name': 'Los Angeles',
  'last_name': 'Angels',
  'primary_color': '003263',
  'secondary_color': 'ba0021',
  'team_id': '3',
  'yahoo_slug': 'la-angels'},
 {'abrv': 'CWS',
  'conference': 'American League',
  'division': 'Central',
  'first_name': 'Chicago',
  'last_name': 'White Sox',
  'primary_color': '27251f',
  'secondary_color': 'c4ced4',
  'team_id': '4',
  'yahoo_slug': 'chi-white-sox'},
 {'abrv': 'CLE',
  'conference': 'American League',
  'division': 'Central',
  'first_name': 'Cleveland',
  'last_name': 'Indians',
  'primary_color': '0c2340',
  'secondary_color': 'e31937',
  'team_id': '5',
  'yahoo_slug': 'cleveland'},
 {'abrv': 'DET',
  'conference': 'American League',
  'division': 'Central',
  'first_name': 'Detroit',
  'last_name': 'Tigers',
  'primary_color': '0c2340',
  'secondary_color': 'fa4616',
  'team_id': '6',
  'yahoo_slug': 'detroit'},
 {'abrv': 'KC',
  'conference': 'American League',
  'division': 'Central',
  'first_name': 'Kansas City',
  'last_name': 'Royals',
  'primary_color': '004687',
  'secondary_color': 'bd9b60',
  'team_id': '7',
  'yahoo_slug': 'kansas-city'},
 {'abrv': 'MIL',
  'conference': 'National League',
  'division': 'Central',
  'first_name': 'Milwaukee',
  'last_name': 'Brewers',
  'primary_color': '0a2351',
  'secondary_color': 'b6922e',
  'team_id': '8',
  'yahoo_slug': 'milwaukee'},
 {'abrv': 'MIN',
  'conference': 'American League',
  'division': 'Central',
  'first_name': 'Minnesota',
  'last_name': 'Twins',
  'primary_color': '002b5c',
  'secondary_color': 'd31145',
  'team_id': '9',
  'yahoo_slug': 'minnesota'}]


stadiums = [('19', 'Dodger Stadium'),
 ('44', 'Minute Maid Park'),
 ('2', 'Fenway Park'),
 ('202', 'Truist Park'),
 ('92', 'Yankee Stadium'),
 ('5', 'Progressive Field'),
 ('46', 'Miller Park'),
 ('16', 'Wrigley Field'),
 ('27', 'Coors Field'),
 ('4', 'Guaranteed Rate'),
 ('47', 'PNC Park'),
 ('11', 'Ring Central'),
 ('89', 'Nationals Park'),
 ('98', 'Marlins Park'),
 ('91', 'Citi Field'),
 ('31', 'Tropicana Field'),
 ('30', 'Chase Field'),
 ('14', 'Rogers Centre'),
 ('41', 'T-Mobile Park'),
 ('45', 'Comerica Park'),
 ('87', 'Busch Stadium'),
 ('83', 'Great American'),
 ('85', 'PETCO Park'),
 ('1', 'Camden Yards'),
 ('3', 'Angel Stadium'),
 ('43', 'Oracle Park'),
 ('84', 'Citizens Bank Park'),
 ('13', 'Globe Life Park'),
 ('96', 'Target Field'),
 ('7', 'Kauffman Stadium'),
 ('205', 'BB&T Ballpark'),
 ('48', 'Bithorn Stadium'),
 ('38', 'Monterrey Stadium'),
 ('42', 'Tokyo Dome'),
 ('206', 'London Stadium'),
 ('207', 'Ameritrade Park'),
 ('29', 'Turner Field'),
 ('201', 'Ft. Bragg Park')]


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


################################################################################
################################################################################


class MLBDB(DB):

    _abrv = "mlb"

    _schema = ("""
                    CREATE TABLE games (
                        game_id INT PRIMARY KEY,
                        home_id INT NOT NULL,
                        away_id INT NOT NULL,
                        winner_id INT NOT NULL,
                        loser_id INT NOT NULL,
                        stadium_id INT NOT NULL,
                        game_type TEXT NOT NULL,
                        season INT NOT NULL,
                        game_year INT NOT NULL,
                        game_date REAL NOT NULL,
                        game_time TEXT NOT NULL,
                        outcome TEXT NOT NULL,
                        FOREIGN KEY (home_id) REFERENCES teams (team_id),
                        FOREIGN KEY (away_id) REFERENCES teams (team_id),
                        FOREIGN KEY (winner_id) REFERENCES teams (team_id),
                        FOREIGN KEY (loser_id) REFERENCES teams (team_id),
                        FOREIGN KEY (stadium_id) REFERENCES stadiums (stadium_id)
                    )
                """,
                """
                    CREATE INDEX idx_season_date ON games (season, game_date)
                """,
                """
                    CREATE TABLE players (
                        player_id INT PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        height INT,
                        weight INT,
                        pos_id INT,
                        bats TEXT,
                        throws TEXT,
                        birth_year INT,
                        birth_day REAL,
                        draft_year INT,
                        draft_pick REAL,
                        draft_team INT,
                        rookie_year INT,
                        FOREIGN KEY (pos_id) REFERENCES position_types (pos_id),
                        FOREIGN KEY (draft_team) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE INDEX idx_names ON players (last_name, first_name)
                """,
                """
                    CREATE TABLE teams (
                        team_id INT PRIMARY KEY,
                        abrv TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        conference TEXT,
                        division TEXT,
                        primary_color TEXT,
                        secondary_color TEXT,
                        yahoo_slug TEXT
                    )
                """,
                """
                    CREATE TABLE stadiums (
                        stadium_id INT PRIMARY KEY,
                        title TEXT
                    )
                """,
                """
                    CREATE TABLE batter_stats (
                        player_id INT NOT NULL,
                        game_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        pa INT NOT NULL,
                        ab INT NOT NULL,
                        bb INT NOT NULL,
                        r INT NOT NULL,
                        h INT NOT NULL,
                        dbl INT NOT NULL,
                        tpl INT NOT NULL,
                        hr INT NOT NULL,
                        tb INT NOT NULL,
                        rbi INT NOT NULL,
                        sb INT NOT NULL,
                        so INT NOT NULL,
                        hbp INT NOT NULL,
                        PRIMARY KEY (player_id, game_id)
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (opp_id)
                    )
                """,
                """
                    CREATE TABLE pitcher_stats (
                        player_id INT NOT NULL,
                        game_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        ip REAL NOT NULL,
                        tot INT NOT NULL,
                        stk INT NOT NULL,
                        gb INT NOT NULL,
                        fb INT NOT NULL,
                        bba INT NOT NULL,
                        ha INT NOT NULL,
                        ra INT NOT NULL,
                        er INT NOT NULL,
                        k INT NOT NULL,
                        hra INT NOT NULL,
                        hbp INT NOT NULL,
                        w INT NOT NULL,
                        l INT NOT NULL,
                        sv INT NOT NULL,
                        blsv INT NOT NULL,
                        PRIMARY KEY (player_id, game_id)
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (opp_id)
                    )
                """,
                """
                    CREATE TABLE team_stats (
                        team_id INT NOT NULL,
                        game_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        ab INT NOT NULL,
                        bb INT NOT NULL,
                        r INT NOT NULL,
                        h INT NOT NULL,
                        hr INT NOT NULL,
                        rbi INT NOT NULL,
                        sb INT NOT NULL,
                        so INT NOT NULL,
                        lob INT NOT NULL,
                        ip REAL NOT NULL,
                        bba INT NOT NULL,
                        ha INT NOT NULL,
                        ra INT NOT NULL,
                        er INT NOT NULL,
                        k INT NOT NULL,
                        hra INT NOT NULL,
                        PRIMARY KEY (team_id, game_id)
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (opp_id)
                    )
                """,
                """
                    CREATE INDEX idx_opp ON team_stats (opp_id, game_id)
                """,
                """
                    CREATE TABLE lineups (
                        lineup_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        batt_order INT NOT NULL,
                        sub_order TEXT NOT NULL,
                        pos TEXT NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE bullpens (
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        pitch_order INT NOT NULL,
                        PRIMARY KEY (player_id, game_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE stat_types (
                        stat_id INT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abrv TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE pitch_types (
                        pitch_type_id INT PRIMARY KEY,
                        title TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE pitch_results (
                        pitch_result_id INT PRIMARY KEY,
                        title TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE pitch_locations (
                        pitch_location_id INT PRIMARY KEY,
                        x_value TEXT NOT NULL,
                        y_value TEXT NOT NULL,
                        box TEXT NOT NULL,
                        strike_zone TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE pitches (
                        pitch_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        pitcher_id INT NOT NULL,
                        batter_id INT NOT NULL,
                        pitch_type_id INT NOT NULL,
                        pitch_location_id INT NOT NULL,
                        pitch_result_id INT NOT NULL,
                        play_num REAL NOT NULL,
                        pitch_num INT NOT NULL,
                        balls INT NOT NULL,
                        strikes INT NOT NULL,
                        sequence INT NOT NULL,
                        pitch_velocity INT NOT NULL,
                        FOREIGN KEY (pitcher_id) REFERENCES players (player_id),
                        FOREIGN KEY (batter_id) REFERENCES players (player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (pitch_type_id) REFERENCES pitch_types (pitch_type_id),
                        FOREIGN KEY (pitch_location_id) REFERENCES pitch_locations (pitch_location_id),
                        FOREIGN KEY (pitch_result_id) REFERENCES pitch_results (pitch_result_id)
                    )
                """,
                """
                    CREATE TABLE ab_types (
                        ab_type_id INT PRIMARY KEY,
                        title TEXT NOT NULL,
                        is_ab INT NOT NULL,
                        on_base INT NOT NULL,
                        is_hit INT NOT NULL,
                        is_out INT NOT NULL,
                        ex_out INT NOT NULL,
                        start_base INT NOT NULL
                    )
                """,
                """
                    CREATE TABLE ab_results (
                        ab_result_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        pitcher_id INT NOT NULL,
                        batter_id INT NOT NULL,
                        pitch_id INT NOT NULL,
                        ab_type_id INT NOT NULL,
                        play_num REAL NOT NULL,
                        hit_style INT,
                        hit_hardness INT,
                        hit_angle INT,
                        hit_distance INT,
                        FOREIGN KEY (pitcher_id) REFERENCES players (player_id),
                        FOREIGN KEY (batter_id) REFERENCES players (player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (pitch_id) REFERENCES pitches (pitch_id),
                        FOREIGN KEY (ab_type_id) REFERENCES ab_types (ab_type_id)
                    )
                """,
                """
                    CREATE TABLE position_types (
                        pos_id INT PRIMARY KEY,
                        abrv TEXT NOT NULL,
                        title TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE game_lines (
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        game_id INT NOT NULL,
                        spread REAL NOT NULL,
                        line INT NOT NULL,
                        money INT NOT NULL,
                        result INT NOT NULL,
                        spread_outcome INT NOT NULL,
                        money_outcome INT NOT NULL,
                        PRIMARY KEY (team_id, game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                """,
                """
                    CREATE TABLE over_unders (
                        game_id INT PRIMARY Key,
                        ou REAL NOT NULL,
                        over_line REAL NOT NULL,
                        under_line REAL NOT NULL,
                        total INT NOT NULL,
                        outcome INT NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                """,
                """
                    CREATE TABLE dk_teams (
                        dk_team_id TEXT PRIMARY KEY,
                        team_id INT NOT NULL,
                        FOREIGN KEY (team_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE dk_players (
                        dk_player_id TEXT NOT NULL,
                        dk_team_id TEXT NOT NULL,
                        player_id INT NOT NULL,
                        PRIMARY KEY (dk_player_id, dk_team_id),
                        FOREIGN KEY (dk_team_id) REFERENCES dk_teams (dk_team_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id)
                    )
                """,
                """
                    CREATE TABLE dk_prices (
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        price INT NOT NULL,
                        PRIMARY KEY (game_id, player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id)
                    )
                """
                )


    def __init__(self):
        super().__init__(DB._dbPath.format(self._abrv))


    def insertGame(self, gameInfo):
        if gameInfo["gameData"]["status_type"] == "final":
            gameData = gameInfo["gameData"]
            gameId = yId(gameData["gameid"])
            homeId = yId(gameData["home_team_id"])
            awayId = yId(gameData["away_team_id"])
            winnerId = yId(gameData["winning_team_id"])
            loserId = homeId if winnerId == awayId else awayId
            season = gameData["season"]
            gameYear = season
            gd = datetime.datetime.strptime(gameData["start_time"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)
            gameDate = "{1}.{2}".format(*str(gd.date()).split("-"))
            gameType = yId(gameData["season_phase_id"])
            gameTime = gameData["start_time"]

            try:
                # Games Table
                self.insert("games", values=[gameId, homeId, awayId, winnerId, loserId, gameData["stadium_id"],
                                                    gameType, season, gameYear, gameDate, gameTime, "won"])

                # Lineups Table
                for side in ("home", "away"):
                    for key, lineup in gameData["lineups"]["{}_lineup".format(side)]["B"].items():

                        lineup["lineup_id"] = None
                        lineup["game_id"] = gameId
                        lineup["player_id"] = yId(lineup["player_id"])
                        lineup["batt_order"] = lineup["order"]
                        lineup["team_id"] = awayId if side == "away" else homeId
                        lineup["opp_id"] = awayId if side == "home" else homeId
                        lineup["sub_order"] = lineup["suborder"]
                        lineup["pos"] = lineup["position"]

                        self.insert("lineups", info=lineup)

                # Bullpens Table
                    for key, bullpen in gameData["lineups"]["{}_lineup".format(side)]["P"].items():
                        bullpen["bullpen_id"] = None
                        bullpen["player_id"] = yId(bullpen["player_id"])
                        bullpen["game_id"] = gameId
                        bullpen["pitch_order"] = bullpen["order"]
                        bullpen["team_id"] = awayId if side == "away" else homeId
                        bullpen["opp_id"] = awayId if side == "home" else homeId
                        self.insert("bullpens", info=bullpen)


                # Team Stats Table
                for teamId, oppId in ((homeId, awayId),(awayId, homeId)):
                    statsData = gameInfo["statsData"]["teamStatsByGameId"]['mlb.g.{}'.format(gameId)]["mlb.t.{}".format(teamId)]['mlb.stat_variation.2']
                    try:
                        teamStats = {}
                        teamStats["team_id"] = teamId
                        teamStats["game_id"] = gameId
                        teamStats["opp_id"] = oppId
                        teamStats["ab"] = statsData["mlb.stat_type.406"]
                        teamStats["bb"] = statsData["mlb.stat_type.415"]
                        teamStats["r"] = statsData["mlb.stat_type.402"]
                        teamStats["h"] = statsData["mlb.stat_type.403"]
                        teamStats["hr"] = statsData["mlb.stat_type.404"]
                        teamStats["rbi"] = statsData["mlb.stat_type.405"]
                        teamStats["sb"] = statsData["mlb.stat_type.409"]
                        teamStats["so"] = statsData["mlb.stat_type.411"]
                        teamStats["lob"] = statsData["mlb.stat_type.416"]
                        inn,third = [int(x) for x in statsData["mlb.stat_type.512"].split(".")]
                        third = third*3333
                        teamStats["ip"] = float("{}.{}".format(inn, third))
                        teamStats["bba"] = statsData["mlb.stat_type.503"]
                        teamStats["ra"] = statsData["mlb.stat_type.505"]
                        teamStats["ha"] = statsData["mlb.stat_type.502"]
                        teamStats["hra"] = statsData["mlb.stat_type.507"]
                        teamStats["er"] = statsData["mlb.stat_type.506"]
                        teamStats["k"] = statsData["mlb.stat_type.504"]

                        self.insert("team_stats", info=teamStats)
                    except KeyError:
                        pass

                # Play Tables
                pitchTemp = {"HBP":0, "SB":0, "CS":0, "TOT":0, "STK":0, "GB":0, "FB":0}
                battTemp = {"PA":0,"HBP":0,"BB":0,"1B":0,"2B":0,"3B":0,"HR":0,"CS":0}
                batters = {}
                pitchers = {}
                batActions = [x[0] for x in atBatResults]



                playerList = [(yId(player["player_id"]), player) for player in gameInfo["playerData"]["players"].values()]
                players = dict(zip([p[0] for p in playerList], [p[1] for p in playerList]))



                pbp = gameData.get("play_by_play",{}).values()
                pitches = gameData.get("pitches",{}).values()

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

                        pitcherStats = pitchers.get(pitcherId, pitchTemp.copy())



                        # Table column entries
                        pitchId = self.nextKey("pitches")
                        try:
                            locationId = self.getKey("pitch_locations", x_value=info["xValue"], y_value =info["yValue"])
                        except OperationalError:
                            locationId = -1
                        # Entering column values into info dictionary
                        for key, value in (("pitch_id", pitchId), ("pitch_location_id", locationId)):
                            info[key] = value

                        pitcherStats["TOT"] += 1
                        if int(info["pitch_result_id"]) > 0:
                            pitcherStats["STK"] += 1

                        pitchers[pitcherId] = pitcherStats

                        self.insert("pitches", info=info)


                    if play["play_type"] == "RESULT":
                        action, _, _ = RP.parseAtBat(play["text"])
                        for i, abResult in enumerate(atBatResults):
                            if abResult[0] == action:
                                # print(action)
                                info["ab_result_id"] = self.nextKey("ab_results")
                                info["ab_type_id"] = i
                                try:
                                    info["pitch_id"] = pitchId
                                except:
                                    print("here")
                                    info["pitch_id"] = -1


                                self.insert("ab_results", info=info)

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

                            if action == "Ground Out":
                                pitcherStats["GB"] += 1
                            elif action in ("Fly Out", "Pop Out", "Line Out", "Foul Out"):
                                pitcherStats["FB"] += 1

                            if action == "Hit by Pitch":
                                pitcherStats["HBP"] += 1
                                batterStats["HBP"] += 1

                            batters[batterId] = batterStats
                            pitchers[pitcherId] = pitcherStats


                for playerId, values in batters.items():
                    try:

                        teamId = yId(players[playerId]["team_id"])
                        oppId = homeId if teamId == awayId else awayId
                    except KeyError:
                        teamId = -1
                        oppId = -1
                    try:
                        stats = gameInfo["statsData"]["playerStats"]["mlb.p.{}".format(playerId)]['mlb.stat_variation.2']
                        values["AB"] = stats["mlb.stat_type.2"]
                        values["R"] = stats["mlb.stat_type.3"]
                        values["H"] = stats["mlb.stat_type.4"]
                        values["SB"] = stats["mlb.stat_type.12"]
                        values["RBI"] = stats["mlb.stat_type.8"]
                        values["SO"] = stats["mlb.stat_type.17"]
                        values["TB"] = values["1B"]+(2*values["2B"]) + (3*values["3B"]) + (4*values["HR"])
                        batterStats = [values[x] for x in ("PA", "AB", "BB", "R", "H", "2B", "3B", "HR", "TB", "RBI", "SB", "SO", "HBP")]

                        self.insert("batter_stats", values=[playerId, gameId, teamId, oppId, *batterStats])
                    except KeyError:
                        pass


                for playerId, values in pitchers.items():
                    try:
                        teamId = yId(players[playerId]["team_id"])
                        oppId = homeId if teamId == awayId else awayId
                    except KeyError:
                        teamId = -1
                        oppId = -1
                    try:
                        stats = gameInfo["statsData"]["playerStats"]["mlb.p.{}".format(playerId)]['mlb.stat_variation.2']


                        inn,third = [int(x) for x in stats["mlb.stat_type.139"].split(".")]
                        third = third*3333
                        values["IP"] = float("{}.{}".format(inn, third))
                        values["BBA"] = stats["mlb.stat_type.118"]
                        values["HA"] = stats["mlb.stat_type.111"]
                        values["RA"] = stats["mlb.stat_type.113"]
                        values["ER"] = stats["mlb.stat_type.114"]
                        values["K"] = stats["mlb.stat_type.121"]
                        values["HRA"] = stats["mlb.stat_type.115"]
                        values["W"] = stats["mlb.stat_type.101"]
                        values["L"] = stats["mlb.stat_type.102"]
                        values["SV"] = stats["mlb.stat_type.107"]
                        values["BLSV"] = stats["mlb.stat_type.147"]


                        pitcherStats = [values[x] for x in ("IP", "TOT", "STK", "GB", "FB", "BBA", "HA", "RA", "ER", "K", "HRA", "HBP", "W", "L", "SV", "BLSV")]

                        self.insert("pitcher_stats", values=[playerId, gameId, teamId, oppId, *pitcherStats])
                    except KeyError:
                        pass

                #### Add Odds
                try:
                    gameData = gameInfo["gameData"]
                    key = [x for x in gameData["odds"].keys()][0]
                    teams = []
                    for hA in ("away", "home"):
                        teamId = yId(gameData["{}_team_id".format(hA)])
                        teamScore = int(gameData["total_{}_points".format(hA)])
                        teamSpread = float(gameData["odds"][key]["{}_spread".format(hA)])
                        teamMoney = gameData["odds"][key]["{}_ml".format(hA)]
                        teamVig = float(gameData["odds"][key]["{}_line".format(hA)])

                        teams.append(dict(zip(("Id", "Score", "Spread", "Money", "Vig"), (teamId, teamScore, teamSpread, teamMoney, teamVig))))

                    #### overUndersTable

                    ou = float(gameData["odds"][key]["total"])
                    overLine = int(gameData["odds"][key]["over_line"])
                    underLine = int(gameData["odds"][key]["under_line"])
                    total = teams[0]["Score"] + teams[1]["Score"]
                    outcome = 0
                    if total - ou > 0:
                        outcome = 1
                    elif total - ou < 0:
                        outcome = -1
                    self.insert("over_unders", values=[gameId, ou, overLine, underLine, total, outcome])


                    #### gameLInesTable

                    for i in range(2):
                        team, opp = teams[-1*i], teams[1+(-1*i)]

                        teamId = team["Id"]
                        oppId = opp["Id"]
                        spread = team["Spread"]
                        line = team["Vig"]
                        money = team["Money"]
                        result = team["Score"] - opp["Score"]
                        spreadOutcome = 0
                        if result + spread > 0:
                            spreadOutcome = 1
                        elif result + spread < 0:
                            spreadOutcome = -1
                        moneyOutcome = 0
                        if result > 0:
                            moneyOutcome = 1
                        elif result < 0:
                            moneyOutcome = -1



                        self.insert("game_lines", values=(teamId, oppId, gameId,
                                                                  spread, line, money, result,
                                                                  spreadOutcome, moneyOutcome))
                except (KeyError, ValueError):
                    pass



            except IntegrityError:
                print("game not added")


    def insertPlayer(self, info):
        playerId = info["player_id"]
        firstName = info["first_name"]
        lastName = info["last_name"]
        height = info["bio"]["height"]
        weight = info["bio"]["weight"]
        bats = info["bat"]
        throws = info["throw"]
        birthYear = info["bio"]["birth_date"].split("-")[0]
        birthDay = "{}.{:2d}".format(*[int(x) for x in info["bio"]["birth_date"].split("-")[1:]])
        try:
            draftYear = info["draft"]["season"]
            if info["draft"]["pick"] =="":
                info["draft"]["pick"] = 0
            draftPick = "{}.{:2d}".format(info["draft"]["round"], int(info["draft"]["pick"]))
            draftTeam = info["draft"]["team_id"]
        except KeyError:
            draftYear = None
            draftPick = None
            draftTeam = None
        except ValueError:
            draftYear = info["draft"]["season"]
            draftPick = None
            draftTeam = info["draft"]["team_id"]


        rookYr = info["bio"]["rookie_season"]
        posId = info["pos_id"]

        self.insert("players", values=(playerId, firstName, lastName, height, weight, posId, bats, throws,
                                        birthYear, birthDay, draftYear, draftPick, draftTeam, rookYr))




    def seed(self):

        print("Seeding teams\n")
        for team in teams:
            self.insert("teams", info=team)

        print("Seeding stadiums\n")
        for stadium in stadiums:
            self.insert("stadiums", values=stadium)

        print("Seeding statTypes\n")
        for stat in statTypes:
            self.insert("stat_types", info=stat)

        print("Seeding pitchLocations\n")
        self.insert("pitch_locations", values=(-1, -1, -1, -1, False))
        for i, location in enumerate(pitchLocations):
            self.insert("pitch_locations", values=(i, *location, sortingHat(*location), str(False if abs(location[0]) > 10000 or abs(location[1]) > 10000 else True)))

        print("Seeding pitchTypes\n")
        for values in pitchTypes:
            self.insert("pitch_types", values=values)

        print("Seeding pitchResults\n")
        for values in pitchResults:
            self.insert("pitch_results", values=values)

        print("Seeding abTypes\n")
        for i, values in enumerate(atBatResults):
            self.insert("ab_types", values=(i, *values))

        print("Seeding positionTypes\n")
        for pos in positions:
            self.insert("position_types", info=pos)

        # print("Seeding players\n")
        # self.insertPlayers()
        #
        # print("Seeding boxscores\n")
        self.insertBoxScores()


    def unknownPlayers(self):

        bCmd = """
                    SELECT DISTINCT player_id
                        FROM batter_stats
                        WHERE player_id NOT IN (SELECT player_id FROM players)
                    """

        pCmd = """
                    SELECT DISTINCT player_id
                        FROM pitcher_stats
                        WHERE player_id NOT IN (SELECT player_id FROM players)
                    """

        return chain([x[0] for x in self.fetchAll(bCmd)], [x[0] for x in self.fetchAll(pCmd)])
