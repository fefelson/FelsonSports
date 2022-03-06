import os
import sqlite3
import re
import datetime

from itertools import chain

from ..Models import DatabaseManager as DB, yId

from sqlite3 import IntegrityError
# for debugging
from pprint import pprint

################################################################################
################################################################################


stadiums = [('2', 'New Era Field'),
             ('3', 'Soldier Field'),
             ('9', 'Lambeau Field'),
             ('12', 'Arrowhead Stadium'),
             ('13', 'Los Angeles Coliseum'),
             ('15', 'Hard Rock Stadium'),
             ('18', 'Superdome'),
             ('23', 'Qualcomm Stadium'),
             ('29', 'Georgia Dome'),
             ('33', 'Bank of America Stadium'),
             ('34', 'RingCentral Coliseum'),
             ('35', 'TIAA Bank Field'),
             ('37', 'Edward Jones Dome'),
             ('40', 'FedEX Field'),
             ('42', 'M&T Bank Stadium'),
             ('43', 'Raymond James Stadium'),
             ('45', 'Nissan Stadium'),
             ('46', 'FirstEnergy Stadium'),
             ('49', 'Paul Brown Stadium'),
             ('50', 'Empower Field'),
             ('51', 'Heinz Field'),
             ('52', 'NRG Stadium'),
             ('53', 'Gillette Stadium'),
             ('55', 'Ford Field'),
             ('56', 'CenturyLink Field'),
             ('58', 'Lincoln Financial Field'),
             ('59', 'Estadio Azteca'),
             ('63', 'State Farm Stadium'),
             ('91', 'Wembley Stadium'),
             ('98', 'Lucas Oil Stadium'),
             ('126', 'AT&T Stadium'),
             ('127', 'MetLife Stadium'),
             ('128', 'MetLife Stadium'),
             ('129', 'TCF Bank Stadium'),
             ('520', 'The Ted'),
             ('1004', "Levi's Stadium"),
             ('1005', 'U.S. Bank Stadium'),
             ('1006', 'Twickenham Stadium'),
             ('1007', 'Dignity Health Sports Park'),
             ('1008', 'Mercedes-Benz Stadium'),
             ('1009', 'Tottenham Hotspur Stadium'),
             ('2454', 'Ford Center')]


statTypes = [{'abrv': 'Fum', 'stat_id': '3', 'title': 'Fumbles Lost'},
             {'abrv': 'PaComp', 'stat_id': '102', 'title': 'Completions'},
             {'abrv': 'PaAtt', 'stat_id': '103', 'title': 'Attempts'},
             {'abrv': 'PaYds', 'stat_id': '105', 'title': 'Yards'},
             {'abrv': 'PaTDs', 'stat_id': '108', 'title': 'Touchdowns'},
             {'abrv': 'PaInts', 'stat_id': '109', 'title': 'Interceptions'},
             {'abrv': 'PaSacks', 'stat_id': '111', 'title': 'Sacks'},
             {'abrv': 'SackYdsL', 'stat_id': '112', 'title': 'Yards Lost'},
             {'abrv': 'QBRat', 'stat_id': '113', 'title': 'QB Rating'},
             {'abrv': 'RuAtt', 'stat_id': '202', 'title': 'Rushes'},
             {'abrv': 'RuYds', 'stat_id': '203', 'title': 'Yards'},
             {'abrv': 'RuTDs', 'stat_id': '207', 'title': 'Touchdowns'},
             {'abrv': 'Rec', 'stat_id': '302', 'title': 'Receptions'},
             {'abrv': 'RecYds', 'stat_id': '303', 'title': 'Yards'},
             {'abrv': 'RecTDs', 'stat_id': '309', 'title': 'Touchdowns'},
             {'abrv': 'Tgt', 'stat_id': '310', 'title': 'Targets'},
             {'abrv': 'FGM', 'stat_id': '407', 'title': 'Total Made'},
             {'abrv': 'FGA', 'stat_id': '408', 'title': 'Total Attempted'},
             {'abrv': 'FGLong', 'stat_id': '410', 'title': 'Long'},
             {'abrv': 'XPM', 'stat_id': '411', 'title': 'Extra Points Made'},
             {'abrv': 'XPA', 'stat_id': '412', 'title': 'Extra Points Attempted'},
             {'abrv': 'Pts', 'stat_id': '413', 'title': 'Points'},
             {'abrv': 'KR', 'stat_id': '502', 'title': 'Kickoff Returns'},
             {'abrv': 'KRYds', 'stat_id': '503', 'title': 'Kick Return Yards'},
             {'abrv': 'KRTDs', 'stat_id': '507', 'title': 'Kick Return Touchdowns'},
             {'abrv': 'PR', 'stat_id': '508', 'title': 'Punt Returns'},
             {'abrv': 'PRYds', 'stat_id': '509', 'title': 'Punt Return Yards'},
             {'abrv': 'PRTDs', 'stat_id': '513', 'title': 'Punt Return Touchdowns'},
             {'abrv': 'Pnt', 'stat_id': '602', 'title': 'Punts'},
             {'abrv': 'PntAvg', 'stat_id': '604', 'title': 'Punt Average'},
             {'abrv': 'PntIn20', 'stat_id': '605', 'title': 'Punts in 20'},
             {'abrv': 'PntTB', 'stat_id': '607', 'title': 'Touchbacks'},
             {'abrv': 'Tkl', 'stat_id': '704', 'title': 'Total Tackles'},
             {'abrv': 'DefSacks', 'stat_id': '705', 'title': 'Sacks'},
             {'abrv': 'DefInts', 'stat_id': '707', 'title': 'Interceptions'},
             {'abrv': 'IntYds', 'stat_id': '708', 'title': 'Yards'},
             {'abrv': 'IntTDs', 'stat_id': '709', 'title': 'Interception Touchdowns'},
             {'abrv': 'PaDef', 'stat_id': '710', 'title': 'Passes Defended'},
             {'abrv': 'FirstD', 'stat_id': '919', 'title': 'First Downs'},
             {'abrv': 'TmRuAtt', 'stat_id': '920', 'title': 'Rushes'},
             {'abrv': 'TmRuYds', 'stat_id': '921', 'title': 'Net Yards Rushing'},
             {'abrv': 'TmINTS', 'stat_id': '926', 'title': 'Interceptions Thrown'},
             {'abrv': 'TmPaSACKS', 'stat_id': '927', 'title': 'Times Sacked'},
             {'abrv': 'TmPaSACKYds', 'stat_id': '928', 'title': 'Yds Lost To Sacks'},
             {'abrv': 'TmPnt', 'stat_id': '929', 'title': 'Punts'},
             {'abrv': 'TmFum', 'stat_id': '932', 'title': 'Fumbles Lost'},
             {'abrv': 'PEN', 'stat_id': '933', 'title': 'Penalties'},
             {'abrv': 'PENYds', 'stat_id': '934', 'title': 'Penalty Yards'},
             {'abrv': 'POSSTIME', 'stat_id': '935', 'title': 'Time of Possession'},
             {'abrv': 'RUSHF', 'stat_id': '936', 'title': 'Rushes for First'},
             {'abrv': 'PASSF', 'stat_id': '937', 'title': 'Passes for First'},
             {'abrv': 'PENF', 'stat_id': '938', 'title': 'Penalties for First'},
             ###
             # {'abrv': '3DE', 'stat_id': '941', 'title': 'Third Down Efficiency'},
             {'abrv': '3DAtt', 'stat_id': '939', 'title': 'Third Down Attempt'},
             {'abrv': '3DComp', 'stat_id': '940', 'title': 'Third Down Complete'},
             # {'abrv': '4DE', 'stat_id': '944', 'title': 'Fourth Down Efficiency'},
             {'abrv': '4DAtt', 'stat_id': '942', 'title': 'Fourth Down Efficiency'},
             {'abrv': '4DComp', 'stat_id': '943', 'title': 'Fourth Down Efficiency'},
             ###
             {'abrv': 'TmYDS', 'stat_id': '945', 'title': 'Total Yards'},
             {'abrv': 'PLAYS', 'stat_id': '946', 'title': 'Total Plays'},
             {'abrv': 'TmPaYds', 'stat_id': '947', 'title': 'Net Yards Passing'},
             {'abrv': 'TO', 'stat_id': '950', 'title': 'Turnovers'},
             ###
             # {'abrv': 'PASSEFF', 'stat_id': '951', 'title': 'Comp-Att'},
             {'abrv': 'TmPaAtt', 'stat_id': '954', 'title': 'Team Pass Attempts'},
             {'abrv': 'TmPaComp', 'stat_id': '953', 'title': 'Team Pass Completions'},
             ###
             {'abrv': 'Points', 'stat_id': '963', 'title': 'Team Points'}]


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
                {"pos_id": "98", "abrv": "KFG", "title": "FG Kicker"},
                {"pos_id": "11", "abrv": "LDE", "title": "Left Defensive End"},
                {"pos_id": "22", "abrv": "K", "title": "Kicker"},
                {"pos_id": "99", "abrv": "KKO", "title": "KO Kicker"},
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


teams = [{'abrv': 'CIN',
  'conference': 'AFC',
  'division': 'North',
  'first_name': 'Cincinnati',
  'last_name': 'Bengals',
  'primary_color': 'fb4f14',
  'secondary_color': '000000',
  'team_id': '4'},
 {'abrv': 'CLE',
  'conference': 'AFC',
  'division': 'North',
  'first_name': 'Cleveland',
  'last_name': 'Browns',
  'primary_color': '311D00',
  'secondary_color': 'FF3C00',
  'team_id': '5'},
 {'abrv': 'DAL',
  'conference': 'NFC',
  'division': 'East',
  'first_name': 'Dallas',
  'last_name': 'Cowboys',
  'primary_color': '002244',
  'secondary_color': 'b0b7bc',
  'team_id': '6'},
 {'abrv': 'DEN',
  'conference': 'AFC',
  'division': 'West',
  'first_name': 'Denver',
  'last_name': 'Broncos',
  'primary_color': 'ff5200',
  'secondary_color': '0a2343',
  'team_id': '7'},
 {'abrv': 'DET',
  'conference': 'NFC',
  'division': 'North',
  'first_name': 'Detroit',
  'last_name': 'Lions',
  'primary_color': '0076B6',
  'secondary_color': 'B0B7BC',
  'team_id': '8'},
 {'abrv': 'GB',
  'conference': 'NFC',
  'division': 'North',
  'first_name': 'Green Bay',
  'last_name': 'Packers',
  'primary_color': '203731',
  'secondary_color': 'FFB612',
  'team_id': '9'},
 {'abrv': 'JAX',
  'conference': 'AFC',
  'division': 'South',
  'first_name': 'Jacksonville',
  'last_name': 'Jaguars',
  'primary_color': '006778',
  'secondary_color': '000000',
  'team_id': '30'},
 {'abrv': 'NYJ',
  'conference': 'AFC',
  'division': 'East',
  'first_name': 'New York',
  'last_name': 'Jets',
  'primary_color': '115740',
  'secondary_color': 'FFFFFF',
  'team_id': '20'},
 {'abrv': 'TEN',
  'conference': 'AFC',
  'division': 'South',
  'first_name': 'Tennessee',
  'last_name': 'Titans',
  'primary_color': '002244',
  'secondary_color': '4b92db',
  'team_id': '10'},
 {'abrv': 'PHI',
  'conference': 'NFC',
  'division': 'East',
  'first_name': 'Philadelphia',
  'last_name': 'Eagles',
  'primary_color': '004C54',
  'secondary_color': 'A5ACAF',
  'team_id': '21'},
 {'abrv': 'IND',
  'conference': 'AFC',
  'division': 'South',
  'first_name': 'Indianapolis',
  'last_name': 'Colts',
  'primary_color': '002c5f',
  'secondary_color': 'a5acaf',
  'team_id': '11'},
 {'abrv': 'ARI',
  'conference': 'NFC',
  'division': 'West',
  'first_name': 'Arizona',
  'last_name': 'Cardinals',
  'primary_color': '97233F',
  'secondary_color': '000000',
  'team_id': '22'},
 {'abrv': 'BAL',
  'conference': 'AFC',
  'division': 'North',
  'first_name': 'Baltimore',
  'last_name': 'Ravens',
  'primary_color': '24135f',
  'secondary_color': '9a7611',
  'team_id': '33'},
 {'abrv': 'KC',
  'conference': 'AFC',
  'division': 'West',
  'first_name': 'Kansas City',
  'last_name': 'Chiefs',
  'primary_color': 'e31837',
  'secondary_color': 'ffb612',
  'team_id': '12'},
 {'abrv': 'PIT',
  'conference': 'AFC',
  'division': 'North',
  'first_name': 'Pittsburgh',
  'last_name': 'Steelers',
  'primary_color': 'ffb612',
  'secondary_color': '000000',
  'team_id': '23'},
 {'abrv': 'HOU',
  'conference': 'AFC',
  'division': 'South',
  'first_name': 'Houston',
  'last_name': 'Texans',
  'primary_color': '03202F',
  'secondary_color': 'A71930',
  'team_id': '34'},
 {'abrv': 'LV',
  'conference': 'AFC',
  'division': 'West',
  'first_name': 'Las Vegas',
  'last_name': 'Raiders',
  'primary_color': '000000',
  'secondary_color': 'a5acaf',
  'team_id': '13'},
 {'abrv': 'LAC',
  'conference': 'AFC',
  'division': 'West',
  'first_name': 'Los Angeles',
  'last_name': 'Chargers',
  'primary_color': '0080c6',
  'secondary_color': 'ffc20e',
  'team_id': '24'},
 {'abrv': 'LAR',
  'conference': 'NFC',
  'division': 'West',
  'first_name': 'Los Angeles',
  'last_name': 'Rams',
  'primary_color': '003594',
  'secondary_color': 'ffd100',
  'team_id': '14'},
 {'abrv': 'SF',
  'conference': 'NFC',
  'division': 'West',
  'first_name': 'San Francisco',
  'last_name': '49ers',
  'primary_color': 'aa0000',
  'secondary_color': 'b3995d',
  'team_id': '25'},
 {'abrv': 'MIA',
  'conference': 'AFC',
  'division': 'East',
  'first_name': 'Miami',
  'last_name': 'Dolphins',
  'primary_color': '008E97',
  'secondary_color': 'fc4c02',
  'team_id': '15'},
 {'abrv': 'SEA',
  'conference': 'NFC',
  'division': 'West',
  'first_name': 'Seattle',
  'last_name': 'Seahawks',
  'primary_color': '002244',
  'secondary_color': '69be28',
  'team_id': '26'},
 {'abrv': 'MIN',
  'conference': 'NFC',
  'division': 'North',
  'first_name': 'Minnesota',
  'last_name': 'Vikings',
  'primary_color': '4F2683',
  'secondary_color': 'FFC62F',
  'team_id': '16'},
 {'abrv': 'TB',
  'conference': 'NFC',
  'division': 'South',
  'first_name': 'Tampa Bay',
  'last_name': 'Buccaneers',
  'primary_color': '322f2b',
  'secondary_color': 'a71930',
  'team_id': '27'},
 {'abrv': 'NE',
  'conference': 'AFC',
  'division': 'East',
  'first_name': 'New England',
  'last_name': 'Patriots',
  'primary_color': '0c2340',
  'secondary_color': 'c8102e',
  'team_id': '17'},
 {'abrv': 'WAS',
  'conference': 'NFC',
  'division': 'East',
  'first_name': 'Washington',
  'last_name': 'Redskins',
  'primary_color': '5a1414',
  'secondary_color': 'ffb612',
  'team_id': '28'},
 {'abrv': 'NO',
  'conference': 'NFC',
  'division': 'South',
  'first_name': 'New Orleans',
  'last_name': 'Saints',
  'primary_color': 'd3bc8d',
  'secondary_color': '000000',
  'team_id': '18'},
 {'abrv': 'CAR',
  'conference': 'NFC',
  'division': 'South',
  'first_name': 'Carolina',
  'last_name': 'Panthers',
  'primary_color': '0085CA',
  'secondary_color': '000000',
  'team_id': '29'},
 {'abrv': 'NYG',
  'conference': 'NFC',
  'division': 'East',
  'first_name': 'New York',
  'last_name': 'Giants',
  'primary_color': '0B2265',
  'secondary_color': 'A71930',
  'team_id': '19'},
 {'abrv': 'ATL',
  'conference': 'NFC',
  'division': 'South',
  'first_name': 'Atlanta',
  'last_name': 'Falcons',
  'primary_color': 'A71930',
  'secondary_color': '000000',
  'team_id': '1'},
 {'abrv': 'BUF',
  'conference': 'AFC',
  'division': 'East',
  'first_name': 'Buffalo',
  'last_name': 'Bills',
  'primary_color': '00338D',
  'secondary_color': 'C60C30',
  'team_id': '2'},
 {'abrv': 'CHI',
  'conference': 'NFC',
  'division': 'North',
  'first_name': 'Chicago',
  'last_name': 'Bears',
  'primary_color': '0B162A',
  'secondary_color': 'e64100',
  'team_id': '3'}]


################################################################################
################################################################################


class NFLDB(DB):

    _abrv = "nfl"

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
                        week INT NOT NULL,
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
                    CREATE INDEX idx_season_date ON games (season, week)
                """,
                """
                    CREATE TABLE players (
                        player_id INT PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        height INT,
                        weight INT,
                        pos_id INT,
                        birth_year INT,
                        birth_day REAL,
                        draft_year INT,
                        draft_pick REAL,
                        draft_team INT,
                        college TEXT,
                        rookie_year INT,
                        FOREIGN KEY (pos_id) REFERENCES positions (pos_id),
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
                        secondary_color TEXT
                    )
                """,
                """
                    CREATE TABLE lineups (
                        player_id INT NOT NULL,
                        game_id INT  NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        PRIMARY KEY (player_id, game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE stadiums (
                        stadium_id INT PRIMARY KEY,
                        title TEXT
                    )
                """,
                """
                    CREATE TABLE player_stats (
                        player_stat_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        stat_id INT NOT NULL,
                        value REAL NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (stat_id) REFERENCES stat_types (stat_id)
                    )
                """,
                """
                    CREATE INDEX idx_player_stats ON player_stats (player_id, game_id, stat_id)
                """,
                """
                    CREATE TABLE team_stats (
                        team_stat_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        stat_id INT NOT NULL,
                        value REAL NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (stat_id) REFERENCES stat_types (stat_id)
                    )
                """,
                """
                    CREATE INDEX idx_team_stats ON team_stats (team_id, game_id, stat_id)
                """,
                """
                    CREATE TABLE stat_types (
                        stat_id INT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abrv TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE positions (
                        pos_id INT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abrv TEXT NOT NULL
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
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
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
                    CREATE TABLE dk_yahoo (
                        dk_id INT NOT NULL,
                        team_id REAL NOT NULL,
                        yahoo_id REAL NOT NULL,
                        PRIMARY KEY (dk_id, team_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (yahoo_id) REFERENCES players (player_id)
                    )
                """,
                """
                    CREATE TABLE line_track (
                        book_name TEXT NOT NULL,
                        game_id INT NOT NULL,
                        away_spread REAL NOT NULL,
                        home_spread REAL NOT NULL,
                        away_line INT,
                        home_line INT,
                        away_ml INT,
                        home_ml INT,
                        total REAL,
                        over_line REAL,
                        under_line REAL,
                        timestamp REAL NOT NULL,
                        PRIMARY KEY (game_id, book_name, timestamp)
                    )
                """
                )


    def __init__(self):
        super().__init__(DB._dbPath.format(self._abrv))


    def insertGame(self, gameInfo):


        #### Add game info
        gameData = gameInfo["gameData"]
        gameId = yId(gameData["gameid"])
        homeId = yId(gameData["home_team_id"])
        awayId = yId(gameData["away_team_id"])
        winnerId = yId(gameData.get("winning_team_id", -1))

        awayPoints = gameData.get("total_away_points", -1)
        homePoints = gameData.get("total_home_points", -1)

        if winnerId == awayId:
            loserId = homeId
        elif winnerId == homeId:
            loserId = awayId
        else:
            loserId = -1
        season = gameData["season"]
        week = int(gameData["week_number"])
        outcome = yId(gameData["outcome_type"])
        gameType = yId(gameData["season_phase_id"])
        gameTime = gameData["start_time"]
        dt = datetime.datetime.strptime(gameData["start_time"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)
        gameYear = dt.year
        gameDate = float("{1}.{2}".format(*str(dt.date()).split("-")))
        self.insert("games", values=[gameId, homeId, awayId, winnerId, loserId, gameData["stadium_id"],
                                            gameType, season, week, gameYear, gameDate, gameTime, outcome])

        ### Lineups Table
        lineups = {}
        for abrv, teamId in (("home", homeId), ("away", awayId)):
            oppId = homeId if teamId == awayId else awayId
            lineups[abrv] = []
            try:
                for playerId in gameData["lineups"]["{}_lineup_order".format(abrv)]["all"]:
                    try:
                        self.insert("lineups", values=[yId(playerId), gameId, teamId, oppId])
                        lineups[abrv].append(yId(playerId))
                    except IntegrityError:
                        continue
            except TypeError:
                pass


        ### Player Stats

        for key, value in gameInfo["statsData"]["playerStats"].items():
            playerId = yId(key)

            if playerId in lineups["home"]:
                teamId = homeId
                oppId = awayId
            elif playerId in lineups["away"]:
                teamId = awayId
                oppId = homeId
            else:
                teamId = -1
                oppId = -1

            for statId, stat in [(yId(k), v) for k, v in value['nfl.stat_variation.2'].items()]:
                if self.checkEntry("stat_types", statId):
                    self.insert("player_stats", values=[None, gameId, playerId, teamId, oppId, statId, stat])


        ### Team Stats
        try:
            self.insert("team_stats", values=[None, gameId, homeId, awayId, 963, homePoints])
            self.insert("team_stats", values=[None, gameId, awayId, homeId, 963, awayPoints])
        except:
            pass

        try:
            teamStats = gameInfo["statsData"]["teamStatsByGameId"]["nfl.g.{}".format(gameId)]
            for teamId, values in [(yId(key), value['nfl.stat_variation.2'].items()) for key, value in teamStats.items()]:
                oppId = homeId if teamId == awayId else awayId

                for statId, stat in [(yId(key), item) for key, item in values]:
                    if self.checkEntry("stat_types", statId):
                        if statId == '935':
                            mins,secs = stat.split(":")[1:]
                            secs = int((int(secs)/60)*100)
                            stat = "{}.{}".format(mins,secs)
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, statId, stat])
                    elif statId == '941':
                        comp,att = stat.split("-")
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, 939, att])
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, 940, comp])
                    elif statId == '944':
                        comp,att = stat.split("-")
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, 942, att])
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, 943, comp])
                    elif statId == '951':
                        comp,att = stat.split("-")
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, 954, att])
                        self.insert("team_stats", values=[None, gameId, teamId, oppId, 953, comp])
        except KeyError:
            pass


        #### Add Odds

        # try:
        gameData = gameInfo["gameData"]
        key = [x for x in gameData["odds"].keys()][0]
        teams = []
        for hA in ("away", "home"):
            teamId = yId(gameData["{}_team_id".format(hA)])
            oppId = homeId if teamId == awayId else awayId
            teamScore = int(gameData["total_{}_points".format(hA)])
            try:
                teamSpread = float(gameData["odds"][key]["{}_spread".format(hA)])
            except:
                teamSpread = 0

            teamMoney = gameData["odds"][key]["{}_ml".format(hA)]
            try:
                teamVig = float(gameData["odds"][key]["{}_line".format(hA)])
            except ValueError:
                teamVig = 0

            teams.append(dict(zip(("Id", "Score", "Spread", "Money", "Vig"), (teamId, teamScore, teamSpread, teamMoney, teamVig))))

        #### overUndersTable

        try:
            ou = float(gameData["odds"][key]["total"])
        except:
            ou = 0

        try:
            overLine = int(gameData["odds"][key]["over_line"])
        except:
            overLine = 0

        try:
            underLine = int(gameData["odds"][key]["under_line"])
        except:
            underLine = 0

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


    def insertPlayer(self, info):
        playerId = info["player_id"]
        firstName = info["first_name"]
        lastName = info["last_name"]
        height = info["bio"]["height"]
        weight = info["bio"]["weight"]

        try:
            birthYear = info["bio"]["birth_date"].split("-")[0]
            birthDay = "{}.{:2d}".format(*[int(x) for x in info["bio"]["birth_date"].split("-")[1:]])
            draftYear = info["draft"]["season"]
            if info["draft"]["pick"] =="":
                info["draft"]["pick"] = 0
            draftPick = "{}.{:2d}".format(info["draft"]["round"], int(info["draft"]["pick"]))
            draftTeam = info["draft"]["team_id"]
        except KeyError:
            draftYear = None
            draftPick = None
            draftTeam = None
        except (IndexError, ValueError):
            birthYear = -1
            birthDay = -1
            draftYear = info["draft"]["season"]
            draftPick = None
            draftTeam = info["draft"]["team_id"]

        college = info.get("college", None)
        rookYr = info["bio"]["rookie_season"]
        posId = info["pos_id"]

        self.insert("players", values=(playerId, firstName, lastName, height, weight, posId, birthYear,
                                        birthDay, draftYear, draftPick, draftTeam, college, rookYr))


    def seed(self):
        for values in stadiums:
            self.insert("stadiums", values=values)

        for info in statTypes:
            self.insert("stat_types", info=info)

        for info in positionTypes:
            self.insert("positions", info=info)

        for team in teams:
            self.insert("teams", info=team)
        self.insert("teams",colNames=("team_id",), values=(-1,))

        # self.insertPlayers()
        # self.insertBoxScores()


    def unknownPlayers(self):

        cmd = """
                SELECT DISTINCT player_id
                    FROM player_stats
                    WHERE player_id NOT IN (SELECT player_id FROM players)
                """
        playerList = []

        return [x[0] for x in self.fetchAll(cmd) if x[0] != None]


################################################################################
################################################################################


class NFLMatchDB(DB):

    _abrv = "nfl"

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
                        week INT NOT NULL,
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
                    CREATE INDEX idx_season_date ON games (season, week)
                """,
                """
                    CREATE TABLE players (
                        player_id INT PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        height INT,
                        weight INT,
                        pos_id INT,
                        birth_year INT,
                        birth_day REAL,
                        draft_year INT,
                        draft_pick REAL,
                        draft_team INT,
                        college TEXT,
                        rookie_year INT,
                        FOREIGN KEY (pos_id) REFERENCES positions (pos_id),
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
                        secondary_color TEXT
                    )
                """,
                """
                    CREATE TABLE lineups (
                        player_id INT NOT NULL,
                        game_id INT  NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        PRIMARY KEY (player_id, game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE stadiums (
                        stadium_id INT PRIMARY KEY,
                        title TEXT
                    )
                """,
                """
                    CREATE TABLE player_stats (
                        player_stat_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        stat_id INT NOT NULL,
                        value REAL NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (stat_id) REFERENCES stat_types (stat_id)
                    )
                """,
                """
                    CREATE INDEX idx_player_stats ON player_stats (player_id, game_id, stat_id)
                """,
                """
                    CREATE TABLE team_stats (
                        team_stat_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        stat_id INT NOT NULL,
                        value REAL NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (stat_id) REFERENCES stat_types (stat_id)
                    )
                """,
                """
                    CREATE INDEX idx_team_stats ON team_stats (team_id, game_id, stat_id)
                """,
                """
                    CREATE TABLE stat_types (
                        stat_id INT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abrv TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE positions (
                        pos_id INT PRIMARY KEY,
                        title TEXT NOT NULL,
                        abrv TEXT NOT NULL
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
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
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
                    CREATE TABLE dk_yahoo (
                        dk_id INT NOT NULL,
                        team_id REAL NOT NULL,
                        yahoo_id REAL NOT NULL,
                        PRIMARY KEY (dk_id, team_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (yahoo_id) REFERENCES players (player_id)
                    )
                """,
                """
                    CREATE TABLE line_track (
                        book_name TEXT NOT NULL,
                        game_id INT NOT NULL,
                        away_spread REAL NOT NULL,
                        home_spread REAL NOT NULL,
                        away_line INT,
                        home_line INT,
                        away_ml INT,
                        home_ml INT,
                        total REAL,
                        over_line REAL,
                        under_line REAL,
                        timestamp REAL NOT NULL,
                        PRIMARY KEY (game_id, book_name, timestamp)
                    )
                """
                )


    def __init__(self, matchPath):
        super().__init__(matchPath)


    def insertGame(self, gameInfo):
        pass



    def insertPlayer(self, info):
        playerId = info["player_id"]
        firstName = info["first_name"]
        lastName = info["last_name"]
        height = info["bio"]["height"]
        weight = info["bio"]["weight"]
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

        college = info.get("college", None)
        rookYr = info["bio"]["rookie_season"]
        posId = info["pos_id"]

        self.insert("players", values=(playerId, firstName, lastName, height, weight, posId, birthYear,
                                        birthDay, draftYear, draftPick, draftTeam, college, rookYr))




    def seed(self):
        for values in stadiums:
            self.insert("stadiums", values=values)

        for info in statTypes:
            self.insert("stat_types", info=info)

        for info in positionTypes:
            self.insert("positions", info=info)

        for team in teams:
            self.insert("teams", info=team)
        self.insert("teams",colNames=("team_id",), values=(-1,))

        # self.insertPlayers()
