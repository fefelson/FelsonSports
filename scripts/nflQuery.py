import sqlite3
from pprint import pprint

nflDBPath = "/home/ededub/FEFelson/NFL.db"
conn = sqlite3.connect(nflDBPath)
curs = conn.cursor()

qbCmd = "SELECT first_name, last_name, "


teamCmd = "SELECT abrv, team_id FROM pro_teams"
curs.execute(teamCmd)

for teamId, abrv in curs.fetchall():
    print(teamId)
    





conn.close()
