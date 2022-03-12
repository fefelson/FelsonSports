import os
import shutil
import tarfile
import json
import datetime
import math

from ..Models import DatabaseManager as DB, yId, normal
from ..Utils import SQL

from pprint import pprint
from sqlite3 import IntegrityError

def getBox(shot):
    basePct = shot["baseline_offset_percentage"] * ((-1) ** int(shot["side_of_basket"] == "R"))
    sidePct = shot["sideline_offset_percentage"]

    box = math.ceil((.5-basePct)/(10/50)) + (5 * int(sidePct/(15/94)))
    box = 1 if box == 0 else box
    return box


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


teams = [{'abrv': 'MIN',
  'conference': 'Western',
  'division': 'Northwest',
  'first_name': 'Minnesota',
  'last_name': 'Timberwolves',
  'primary_color': '0c2340',
  'secondary_color': '236192',
  'team_id': '16',
  'yahoo_slug': 'minnesota'},
 {'abrv': 'WAS',
  'conference': 'Eastern',
  'division': 'Southeast',
  'first_name': 'Washington',
  'last_name': 'Wizards',
  'primary_color': '002b5c',
  'secondary_color': 'e31837',
  'team_id': '27',
  'yahoo_slug': 'washington'},
 {'abrv': 'BKN',
  'conference': 'Eastern',
  'division': 'Atlantic',
  'first_name': 'Brooklyn',
  'last_name': 'Nets',
  'primary_color': '000000',
  'secondary_color': 'ffffff',
  'team_id': '17',
  'yahoo_slug': 'brooklyn'},
 {'abrv': 'TOR',
  'conference': 'Eastern',
  'division': 'Atlantic',
  'first_name': 'Toronto',
  'last_name': 'Raptors',
  'primary_color': 'ce1141',
  'secondary_color': '000000',
  'team_id': '28',
  'yahoo_slug': 'toronto'},
 {'abrv': 'NY',
  'conference': 'Eastern',
  'division': 'Atlantic',
  'first_name': 'New York',
  'last_name': 'Knicks',
  'primary_color': '006bb6',
  'secondary_color': 'f58426',
  'team_id': '18',
  'yahoo_slug': 'new-york'},
 {'abrv': 'MEM',
  'conference': 'Western',
  'division': 'Southwest',
  'first_name': 'Memphis',
  'last_name': 'Grizzlies',
  'primary_color': '5d76a9',
  'secondary_color': '12173f',
  'team_id': '29',
  'yahoo_slug': 'memphis'},
 {'abrv': 'ORL',
  'conference': 'Eastern',
  'division': 'Southeast',
  'first_name': 'Orlando',
  'last_name': 'Magic',
  'primary_color': '0077c0',
  'secondary_color': 'c4ced4',
  'team_id': '19',
  'yahoo_slug': 'orlando'},
 {'abrv': 'ATL',
  'conference': 'Eastern',
  'division': 'Southeast',
  'first_name': 'Atlanta',
  'last_name': 'Hawks',
  'primary_color': 'e03a3e',
  'secondary_color': 'c1d32f',
  'team_id': '1',
  'yahoo_slug': 'atlanta'},
 {'abrv': 'BOS',
  'conference': 'Eastern',
  'division': 'Atlantic',
  'first_name': 'Boston',
  'last_name': 'Celtics',
  'primary_color': '007a33',
  'secondary_color': 'ba9653',
  'team_id': '2',
  'yahoo_slug': 'boston'},
 {'abrv': 'NO',
  'conference': 'Western',
  'division': 'Southwest',
  'first_name': 'New Orleans',
  'last_name': 'Pelicans',
  'primary_color': '0c2340',
  'secondary_color': 'c8102e',
  'team_id': '3',
  'yahoo_slug': 'new-orleans'},
 {'abrv': 'CHA',
  'conference': 'Eastern',
  'division': 'Southeast',
  'first_name': 'Charlotte',
  'last_name': 'Hornets',
  'primary_color': '1D1160',
  'secondary_color': '00788c',
  'team_id': '30',
  'yahoo_slug': 'charlotte'},
 {'abrv': 'CHI',
  'conference': 'Eastern',
  'division': 'Central',
  'first_name': 'Chicago',
  'last_name': 'Bulls',
  'primary_color': 'ce1141',
  'secondary_color': '000000',
  'team_id': '4',
  'yahoo_slug': 'chicago'},
 {'abrv': 'PHI',
  'conference': 'Eastern',
  'division': 'Atlantic',
  'first_name': 'Philadelphia',
  'last_name': '76ers',
  'primary_color': '006bb6',
  'secondary_color': 'ed174c',
  'team_id': '20',
  'yahoo_slug': 'philadelphia'},
 {'abrv': 'CLE',
  'conference': 'Eastern',
  'division': 'Central',
  'first_name': 'Cleveland',
  'last_name': 'Cavaliers',
  'primary_color': '6f263d',
  'secondary_color': '041e42',
  'team_id': '5',
  'yahoo_slug': 'cleveland'},
 {'abrv': 'HOU',
  'conference': 'Western',
  'division': 'Southwest',
  'first_name': 'Houston',
  'last_name': 'Rockets',
  'primary_color': 'ce1141',
  'secondary_color': '000000',
  'team_id': '10',
  'yahoo_slug': 'houston'},
 {'abrv': 'PHO',
  'conference': 'Western',
  'division': 'Pacific',
  'first_name': 'Phoenix',
  'last_name': 'Suns',
  'primary_color': '1d1160',
  'secondary_color': 'e56020',
  'team_id': '21',
  'yahoo_slug': 'phoenix'},
 {'abrv': 'DAL',
  'conference': 'Western',
  'division': 'Southwest',
  'first_name': 'Dallas',
  'last_name': 'Mavericks',
  'primary_color': '00538c',
  'secondary_color': '002b5e',
  'team_id': '6',
  'yahoo_slug': 'dallas'},
 {'abrv': 'IND',
  'conference': 'Eastern',
  'division': 'Central',
  'first_name': 'Indiana',
  'last_name': 'Pacers',
  'primary_color': '002d62',
  'secondary_color': 'fdbb30',
  'team_id': '11',
  'yahoo_slug': 'indiana'},
 {'abrv': 'POR',
  'conference': 'Western',
  'division': 'Northwest',
  'first_name': 'Portland',
  'last_name': 'Trail Blazers',
  'primary_color': 'e03a3e',
  'secondary_color': '000000',
  'team_id': '22',
  'yahoo_slug': 'portland'},
 {'abrv': 'DEN',
  'conference': 'Western',
  'division': 'Northwest',
  'first_name': 'Denver',
  'last_name': 'Nuggets',
  'primary_color': '0e2240',
  'secondary_color': 'fec524',
  'team_id': '7',
  'yahoo_slug': 'denver'},
 {'abrv': 'LAC',
  'conference': 'Western',
  'division': 'Pacific',
  'first_name': 'Los Angeles',
  'last_name': 'Clippers',
  'primary_color': 'c8102e',
  'secondary_color': '1d42ba',
  'team_id': '12',
  'yahoo_slug': 'la-clippers'},
 {'abrv': 'SAC',
  'conference': 'Western',
  'division': 'Pacific',
  'first_name': 'Sacramento',
  'last_name': 'Kings',
  'primary_color': '5a2d81',
  'secondary_color': '63727a',
  'team_id': '23',
  'yahoo_slug': 'sacramento'},
 {'abrv': 'DET',
  'conference': 'Eastern',
  'division': 'Central',
  'first_name': 'Detroit',
  'last_name': 'Pistons',
  'primary_color': 'c8102e',
  'secondary_color': '006bb6',
  'team_id': '8',
  'yahoo_slug': 'detroit'},
 {'abrv': 'LAL',
  'conference': 'Western',
  'division': 'Pacific',
  'first_name': 'Los Angeles',
  'last_name': 'Lakers',
  'primary_color': '552583',
  'secondary_color': 'fdb927',
  'team_id': '13',
  'yahoo_slug': 'la-lakers'},
 {'abrv': 'SA',
  'conference': 'Western',
  'division': 'Southwest',
  'first_name': 'San Antonio',
  'last_name': 'Spurs',
  'primary_color': 'c4ced4',
  'secondary_color': '000000',
  'team_id': '24',
  'yahoo_slug': 'san-antonio'},
 {'abrv': 'GS',
  'conference': 'Western',
  'division': 'Pacific',
  'first_name': 'Golden State',
  'last_name': 'Warriors',
  'primary_color': '1d428a',
  'secondary_color': 'FDB927',
  'team_id': '9',
  'yahoo_slug': 'golden-state'},
 {'abrv': 'MIA',
  'conference': 'Eastern',
  'division': 'Southeast',
  'first_name': 'Miami',
  'last_name': 'Heat',
  'primary_color': '98002e',
  'secondary_color': 'f9a01b',
  'team_id': '14',
  'yahoo_slug': 'miami'},
 {'abrv': 'OKC',
  'conference': 'Western',
  'division': 'Northwest',
  'first_name': 'Oklahoma City',
  'last_name': 'Thunder',
  'primary_color': '007ac1',
  'secondary_color': 'ef3b24',
  'team_id': '25',
  'yahoo_slug': 'oklahoma-city'},
 {'abrv': 'MIL',
  'conference': 'Eastern',
  'division': 'Central',
  'first_name': 'Milwaukee',
  'last_name': 'Bucks',
  'primary_color': '00471b',
  'secondary_color': 'eee1c6',
  'team_id': '15',
  'yahoo_slug': 'milwaukee'},
 {'abrv': 'UTA',
  'conference': 'Western',
  'division': 'Northwest',
  'first_name': 'Utah',
  'last_name': 'Jazz',
  'primary_color': '002b5c',
  'secondary_color': '00471b',
  'team_id': '26',
  'yahoo_slug': 'utah'}
  ]


class NBADB(DB):

    _abrv = "nba"

    _schema = ("""
                    CREATE TABLE games (
                        game_id INT PRIMARY KEY,
                        home_id INT NOT NULL,
                        away_id INT NOT NULL,
                        winner_id INT NOT NULL,
                        loser_id INT NOT NULL,
                        game_type TEXT NOT NULL,
                        season INT NOT NULL,
                        game_year INT NOT NULL,
                        game_date REAL NOT NULL,
                        game_time TEXT NOT NULL,
                        outcome TEXT NOT NULL,
                        FOREIGN KEY (home_id) REFERENCES teams (team_id),
                        FOREIGN KEY (away_id) REFERENCES teams (team_id),
                        FOREIGN KEY (winner_id) REFERENCES teams (team_id),
                        FOREIGN KEY (loser_id) REFERENCES teams (team_id)
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
                        birth_year INT,
                        birth_day REAL,
                        draft_year INT,
                        draft_pick REAL,
                        draft_team INT,
                        college TEXT,
                        rookie_year INT,
                        FOREIGN KEY (pos_id) REFERENCES position_types (pos_id),
                        FOREIGN KEY (draft_team) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE INDEX idx_names ON players (last_name, first_name)
                """,
                """
                    CREATE TABLE player_positions (
                        player_id INT NOT NULL,
                        pos_id INT NOT NULL,
                        PRIMARY KEY (player_id, pos_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (pos_id) REFERENCES position_types (pos_id)
                    )
                """,
                """
                    CREATE TABLE teams (
                        team_id INT PRIMARY KEY,
                        abrv TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        conference TEXT NOT NULL,
                        division TEXT NOT NULL,
                        primary_color TEXT NOT NULL,
                        secondary_color TEXT NOT NULL,
                        yahoo_slug TEXT
                    )
                """,
                """
                    CREATE TABLE lineups (
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        starter INT NOT NULL,
                        active INT NOT NULL,
                        PRIMARY KEY(game_id, player_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE player_stats (
                        player_id INT NOT NULL,
                        game_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        fga INT NOT NULL,
                        fgm INT NOT NULL,
                        fta INT NOT NULL,
                        ftm INT NOT NULL,
                        tpa INT NOT NULL,
                        tpm INT NOT NULL,
                        pts INT NOT NULL,
                        oreb INT NOT NULL,
                        dreb INT NOT NULL,
                        reb INT NOT NULL,
                        ast INT NOT NULL,
                        stl INT NOT NULL,
                        blk INT NOT NULL,
                        trn INT NOT NULL,
                        fls INT NOT NULL,
                        tfl INT NOT NULL,
                        ejs INT NOT NULL,
                        ff INT NOT NULL,
                        mins INT NOT NULL,
                        plmn INT NOT NULL,
                        ba INT NOT NULL,
                        PRIMARY KEY (player_id, game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE player_shots (
                        player_shot_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        assist_id INT NOT NULL,
                        block_id TEXT NOT NULL,
                        pts INT NOT NULL,
                        made INT NOT NULL,
                        base_pct REAL NOT NULL,
                        side_pct REAL NOT NULL,
                        box INT NOT NULL,
                        distance INT NOT NULL,
                        fastbreak INT NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (assist_id) REFERENCES players (player_id),
                        FOREIGN KEY (block_id) REFERENCES players (player_id)
                    )
                """,
                """
                    CREATE INDEX idx_shots_players ON player_shots (player_id, game_id)
                """,
                """
                    CREATE INDEX idx_opp_shots ON player_shots (opp_id, game_id)
                """,
                """
                    CREATE TABLE team_stats (
                        team_id INT NOT NULL,
                        game_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        b2b INT NOT NULL,
                        fga INT NOT NULL,
                        fgm INT NOT NULL,
                        fta INT NOT NULL,
                        ftm INT NOT NULL,
                        tpa INT NOT NULL,
                        tpm INT NOT NULL,
                        pts INT NOT NULL,
                        oreb INT NOT NULL,
                        dreb INT NOT NULL,
                        reb INT NOT NULL,
                        ast INT NOT NULL,
                        stl INT NOT NULL,
                        blk INT NOT NULL,
                        trn INT NOT NULL,
                        fls INT NOT NULL,
                        pts_in_pt INT NOT NULL,
                        fb_pts INT NOT NULL,
                        PRIMARY KEY (team_id, game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE INDEX idx_opp_stats ON team_stats (opp_id, game_id)
                """,
                """
                    CREATE TABLE position_types (
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

        #### Add game info
        gameData = gameInfo["gameData"]
        gameId = yId(gameData["gameid"])
        homeId = yId(gameData["home_team_id"])
        awayId = yId(gameData["away_team_id"])
        winnerId = yId(gameData["winning_team_id"])
        loserId = homeId if winnerId == awayId else awayId
        season = gameData["season"]
        gd = datetime.datetime.strptime(gameData["start_time"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)
        gameDate = "{1}.{2}".format(*str(gd.date()).split("-"))

        gameYear = gd.year
        gameType = yId(gameData["season_phase_id"])
        gameTime = gameData["start_time"]
        self.insert("games", values=[gameId, homeId, awayId, winnerId, loserId,
                                            gameType, season, gameYear, gameDate, gameTime, "won"])

        #### Add team stats
        try:
            statsData = gameInfo["statsData"]["teamStatsByGameId"]["nba.g.{}".format(gameId)]
            for teamId in (homeId, awayId):
                oppId = homeId if teamId == awayId else awayId
                teamStats = statsData["nba.t.{}".format(teamId)]["nba.stat_variation.2"]


                yesterday = gd - datetime.timedelta(1)
                b2b = 1 if self.fetchItem(SQL.b2bCmd, (gameYear, "{}.{}".format(*str(yesterday).split("-")[1:]), teamId)) else 0
                fga = teamStats["nba.stat_type.104"]
                fgm = teamStats["nba.stat_type.105"]
                fta = teamStats["nba.stat_type.107"]
                ftm = teamStats["nba.stat_type.108"]
                tpa = teamStats["nba.stat_type.110"]
                tpm = teamStats["nba.stat_type.111"]
                pts = teamStats["nba.stat_type.113"]
                oreb = teamStats["nba.stat_type.114"]
                dreb = teamStats["nba.stat_type.115"]
                reb = teamStats["nba.stat_type.116"]
                ast = teamStats["nba.stat_type.117"]
                stl = teamStats["nba.stat_type.118"]
                blk = teamStats["nba.stat_type.119"]
                trn = teamStats["nba.stat_type.120"]
                fls = teamStats["nba.stat_type.122"]
                fb = sum([int(x["points"])*int(x["shot_made"])*int(x["fastbreak"]) for x in gameData["play_by_play"].values() if x["class_type"] == "SHOT" and x["team"] == teamId])
                paint = sum([int(x["points"])*int(x["shot_made"]) for x in gameData["play_by_play"].values() if x["class_type"] == "SHOT" and x["team"] == teamId and (getBox(x) == 3 or getBox(x) == 8)])
                self.insert("team_stats", values=[teamId, gameId, oppId, b2b, fga, fgm, fta, ftm,
                                                        tpa, tpm, pts, oreb, dreb, reb, ast, stl, blk, trn, fls,
                                                        paint, fb])
        except KeyError:
            pass

        #### Set rosters
        roster = {}
        playerTeam = gameData["playersByTeam"]
        for key in playerTeam.keys():
            teamId = yId(key)
            for player in playerTeam[key]:
                roster[yId(player)] = teamId


        ### Add lineup stats

        try:
            pgData = gameData["lineups"]
            for lineup in ("away_lineup", "home_lineup"):
                for key, value in pgData[lineup]["all"].items():
                    playerId = yId(key)
                    teamId = roster.get(playerId, -1)
                    oppId = homeId if teamId == awayId else awayId
                    if teamId == -1:
                        oppId = -1
                    active = value.get("active", -1)
                    starter = value.get("starter", -1)
                    try:
                        self.insert("lineups", values=[gameId, playerId, teamId, oppId, starter, active])
                    except IntegrityError:
                        print([gameId, playerId, teamId, oppId, starter, active])
        except TypeError:
            pass


        #### Add player stats

        statsData = gameInfo["statsData"]["playerStats"]
        for key, value in statsData.items():
            playerId = yId(key)
            teamId = roster.get(playerId, -1)
            oppId = homeId if teamId == awayId else awayId
            if teamId == -1:
                oppId = -1
            playerStats = value["nba.stat_variation.2"]
            fgm, fga = playerStats.pop("nba.stat_type.28").split("-")
            ftm, fta = playerStats.pop("nba.stat_type.29").split("-")
            tpm, tpa = playerStats.pop("nba.stat_type.30").split("-")
            pts = playerStats["nba.stat_type.13"]
            oreb = playerStats["nba.stat_type.14"]
            dreb = playerStats["nba.stat_type.15"]
            reb = playerStats["nba.stat_type.16"]
            ast = playerStats["nba.stat_type.17"]
            stl = playerStats["nba.stat_type.18"]
            blk = playerStats["nba.stat_type.19"]
            trn = playerStats["nba.stat_type.20"]
            fls = playerStats["nba.stat_type.22"]
            tfl = playerStats["nba.stat_type.24"]
            ejs = playerStats["nba.stat_type.25"]
            ff = playerStats["nba.stat_type.26"]
            ms,sec = playerStats["nba.stat_type.3"].split(":")
            sec = round((int(sec)/60)*100)
            mins = "{}.{}".format(ms, sec)
            plmin = playerStats["nba.stat_type.32"]
            ba = playerStats["nba.stat_type.33"]

            self.insert("player_stats", values=[playerId, gameId, teamId, oppId, fga, fgm, fta, ftm,
                                                    tpa, tpm, pts, oreb, dreb, reb, ast, stl, blk, trn, fls,
                                                    tfl, ejs, ff, mins, plmin, ba])

        #### Add player shots

        try:
            statsData = gameInfo["gameData"]["play_by_play"]

            for x in [x for x in statsData.values() if x["class_type"] == "SHOT" and int(x["points"]) > 1]:

                teamId = x["team"]
                playerId = x["player"]
                oppId = homeId if teamId == awayId else awayId
                assistId = x["assister"]
                blockId = x["blocker"]
                pts = x["points"]
                made = x["shot_made"]
                basePct = x["baseline_offset_percentage"] * ((-1) ** int(x["side_of_basket"] == "R"))
                sidePct = x["sideline_offset_percentage"]

                box = math.ceil((.5-basePct)/(10/50)) + (5 * int(sidePct/(15/94)))
                box = 1 if box == 0 else box
                distance = int(math.sqrt( (50*basePct)**2 + (sidePct*94)**2  ))
                fastbreak = x["fastbreak"]

                self.insert("player_shots", values=[None, gameId, playerId,
                                                          teamId, oppId, assistId, blockId,
                                                          pts, made, basePct,
                                                          sidePct, box, distance,
                                                          fastbreak])
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
            birthYear = info["bio"]["birth_date"].split("-")[0]
            birthDay = "{}.{:2d}".format(*[int(x) for x in info["bio"]["birth_date"].split("-")[1:]])
            draftYear = None
            draftPick = None
            draftTeam = None
        except ValueError:
            birthYear = info["bio"]["birth_date"].split("-")[0]
            birthDay = "{}.{:2d}".format(*[int(x) for x in info["bio"]["birth_date"].split("-")[1:]])
            draftYear = info["draft"]["season"]
            draftPick = None
            draftTeam = info["draft"]["team_id"]
        except IndexError:
            birthYear = -1
            birthDay = -1
            draftYear = None
            draftPick = None
            draftTeam = None


        college = info.get("college", None)
        rookYr = info["bio"]["rookie_season"]
        posId = info["pos_id"]

        self.insert("players", values=(playerId, firstName, lastName, height, weight, posId, birthYear,
                                        birthDay, draftYear, draftPick, draftTeam, college, rookYr))


    def seed(self):

        print("Seeding position types\n")
        for position in positions:
            self.insert("position_types", info=position)

        print("Seeding teams\n")
        for team in teams:
            self.insert("teams", info=team)

        print("Seeding players\n")
        self.insertPlayers()
        print("Seeding boxscores\n")
        self.insertBoxScores()


    def unknownPlayers(self):
        cmd = """
                SELECT DISTINCT player_id
                    FROM player_stats
                    WHERE player_id NOT IN (SELECT player_id FROM players)
                """
        return [x[0] for x in self.fetchAll(cmd)]


#################################################################################
#################################################################################


class NBAMatchDB(DB):
    _abrv = "nba"

    _schema = ("""
                    CREATE TABLE games (
                        game_id INT PRIMARY KEY,
                        home_id INT NOT NULL,
                        away_id INT NOT NULL,
                        winner_id INT NOT NULL,
                        loser_id INT NOT NULL,
                        game_type TEXT NOT NULL,
                        season INT NOT NULL,
                        game_year INT NOT NULL,
                        game_date REAL NOT NULL,
                        game_time TEXT NOT NULL,
                        outcome TEXT NOT NULL,
                        FOREIGN KEY (home_id) REFERENCES teams (team_id),
                        FOREIGN KEY (away_id) REFERENCES teams (team_id),
                        FOREIGN KEY (winner_id) REFERENCES teams (team_id),
                        FOREIGN KEY (loser_id) REFERENCES teams (team_id)
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
                        birth_year INT,
                        birth_day REAL,
                        draft_year INT,
                        draft_pick REAL,
                        draft_team INT,
                        college TEXT,
                        rookie_year INT,
                        FOREIGN KEY (pos_id) REFERENCES position_types (pos_id),
                        FOREIGN KEY (draft_team) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE INDEX idx_names ON players (last_name, first_name)
                """,
                """
                    CREATE TABLE player_positions (
                        player_id INT NOT NULL,
                        pos_id INT NOT NULL,
                        PRIMARY KEY (player_id, pos_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (pos_id) REFERENCES position_types (pos_id)
                    )
                """,
                """
                    CREATE TABLE teams (
                        team_id INT PRIMARY KEY,
                        abrv TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        conference TEXT NOT NULL,
                        division TEXT NOT NULL,
                        primary_color TEXT NOT NULL,
                        secondary_color TEXT NOT NULL,
                        yahoo_slug TEXT
                    )
                """,
                """
                    CREATE TABLE lineups (
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        starter INT NOT NULL,
                        active INT NOT NULL,
                        PRIMARY KEY(game_id, player_id)
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE player_stats (
                        player_id INT NOT NULL,
                        game_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        fga INT NOT NULL,
                        fgm INT NOT NULL,
                        fta INT NOT NULL,
                        ftm INT NOT NULL,
                        tpa INT NOT NULL,
                        tpm INT NOT NULL,
                        pts INT NOT NULL,
                        oreb INT NOT NULL,
                        dreb INT NOT NULL,
                        reb INT NOT NULL,
                        ast INT NOT NULL,
                        stl INT NOT NULL,
                        blk INT NOT NULL,
                        trn INT NOT NULL,
                        fls INT NOT NULL,
                        tfl INT NOT NULL,
                        ejs INT NOT NULL,
                        ff INT NOT NULL,
                        mins INT NOT NULL,
                        plmn INT NOT NULL,
                        ba INT NOT NULL,
                        PRIMARY KEY (player_id, game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE TABLE player_shots (
                        player_shot_id INT PRIMARY KEY,
                        game_id INT NOT NULL,
                        player_id INT NOT NULL,
                        team_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        assist_id INT NOT NULL,
                        block_id TEXT NOT NULL,
                        pts INT NOT NULL,
                        made INT NOT NULL,
                        base_pct REAL NOT NULL,
                        side_pct REAL NOT NULL,
                        box INT NOT NULL,
                        distance INT NOT NULL,
                        fastbreak INT NOT NULL,
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id),
                        FOREIGN KEY (assist_id) REFERENCES players (player_id),
                        FOREIGN KEY (block_id) REFERENCES players (player_id)
                    )
                """,
                """
                    CREATE INDEX idx_shots_players ON player_shots (player_id, game_id)
                """,
                """
                    CREATE INDEX idx_opp_shots ON player_shots (opp_id, game_id)
                """,
                """
                    CREATE TABLE team_stats (
                        team_id INT NOT NULL,
                        game_id INT NOT NULL,
                        opp_id INT NOT NULL,
                        b2b INT NOT NULL,
                        fga INT NOT NULL,
                        fgm INT NOT NULL,
                        fta INT NOT NULL,
                        ftm INT NOT NULL,
                        tpa INT NOT NULL,
                        tpm INT NOT NULL,
                        pts INT NOT NULL,
                        oreb INT NOT NULL,
                        dreb INT NOT NULL,
                        reb INT NOT NULL,
                        ast INT NOT NULL,
                        stl INT NOT NULL,
                        blk INT NOT NULL,
                        trn INT NOT NULL,
                        fls INT NOT NULL,
                        pts_in_pt INT NOT NULL,
                        fb_pts INT NOT NULL,
                        PRIMARY KEY (team_id, game_id),
                        FOREIGN KEY (team_id) REFERENCES teams (team_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id),
                        FOREIGN KEY (opp_id) REFERENCES teams (team_id)
                    )
                """,
                """
                    CREATE INDEX idx_opp_stats ON team_stats (opp_id, game_id)
                """,
                """
                    CREATE TABLE position_types (
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
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                """,
                """
                    CREATE TABLE history_lines (
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

    def __init__(self, matchPath):
        super().__init__(matchPath)


    def insertGame(self):
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

        print("Seeding position types\n")
        for position in positions:
            self.insert("position_types", info=position)

        print("Seeding teams\n")
        for team in teams:
            self.insert("teams", info=team)

        # print("Seeding players\n")
        # self.insertPlayers()
