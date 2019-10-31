import csv
import sqlite3
from pprint import pprint
from json import load

##
mlbDBPath = "/home/ededub/FEFelson/MLB.db"
##dkPath = "/home/ededub/FEFelson/Fantasy/Draftkings/MLB/"
##scorePath = "/home/ededub/FEFelson/MLB/BoxScores/{}/{}/{}/scoreboard.json"
##gamePath = "/home/ededub/FEFelson/MLB/BoxScores/{}/{}/{}/M{}.json"
##csvPath = "/home/ededub/Downloads/DKSalaries ({}).csv"
####
##players = []
##teams = []
##for page in range(50,55):
##    with open(csvPath.format(page)) as f:
##        f_csv = csv.reader(f)
##        for i, row in enumerate(f_csv):
##            if i > 0:
##                players.append(row[2])
##                for team in row[6].split()[0].split("@"):
##                    if team not in teams:
##                        teams.append(team)
##
##
##pprint(teams)
##
##
##
##
##
##
##
##
conn = sqlite3.connect(mlbDBPath)
curs = conn.cursor()
##
##
##cmd = "CREATE TABLE IF NOT EXISTS dk_players (dk_id TEXT PRIMARY KEY, player_id TEXT NOT NULL, FOREIGN KEY (player_id) REFERENCES pro_players (player_id))"
##curs.execute(cmd)
##conn.commit()
##
##cmd = "CREATE TABLE IF NOT EXISTS dk_teams (abrv TEXT PRIMARY KEY, team_id TEXT NOT NULL, FOREIGN KEY (team_id) REFERENCES pro_teams (team_id))"
##curs.execute(cmd)
##conn.commit()
##
##for team in teams:
##    try:
##        cmd = "SELECT team_id FROM pro_teams WHERE abrv = ?"
##        curs.execute(cmd, (team.lower(),))
##        teamId = curs.fetchone()[0]
##    except TypeError:
##        print(team)
##        cmd = "SELECT team_id, abrv FROM pro_teams"
##        curs.execute(cmd)
##        pprint(curs.fetchall())
##        teamId = input()
##    cmd = "INSERT INTO dk_teams VALUES(?,?)"
##    curs.execute(cmd, (team, teamId))
##conn.commit()
##
##for player in set(players):
##    cmd = "SELECT * FROM dk_players WHERE dk_id = ?"
##    curs.execute(cmd, (player,))
##    if not curs.fetchone():
##        try:
##            first, last = player.split()
##        except ValueError:
##            index = int(input(player.split()))
##            first = " ".join(player.split()[:index])
##            last = " ".join(player.split()[index:])
##        print(first, last)
##
##        cmd = "SELECT player_id FROM pro_players WHERE first_name = ? AND last_name = ?"
##        curs.execute(cmd,(first,last))
##        try:
##            playerId = curs.fetchone()[0]
##        except TypeError:
##            playerId = "-1"
##        if playerId != "-1":
##            cmd = "INSERT INTO dk_players VALUES(?,?)"
##            curs.execute(cmd,(player,playerId))
##            conn.commit()

updates = (("R", "Erick", "Fedde"),
           
           
           )


cmd = "UPDATE pro_players SET throws = ? WHERE first_name = ? AND last_name = ?"
for x in updates:
    curs.execute(cmd, x)


##cmd = "SELECT first_name, last_name, throws FROM pro_players INNER JOIN pitcher_vs_batter ON pro_players.player_id = pitcher_vs_batter.pitcher_id WHERE hr >= 1 AND batter_id = (SELECT player_id FROM pro_players WHERE first_name = 'Giancarlo')"
##curs.execute(cmd)
##pprint(curs.fetchall())

conn.commit()
conn.close()
           




    
