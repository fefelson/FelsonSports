import sqlite3
from matplotlib import pyplot as plt

conn = sqlite3.connect("/home/ededub/FEFelson/NBA/NBA.db")
curs = conn.cursor()

cmd = "SELECT teams.abrv, AVG(teamStats.pts) FROM teams, teamStats, games WHERE teams.teamId = teamStats.teamId AND games.gameId = teamStats.gameId AND games.season = 2018 GROUP BY teams.teamId"
curs.execute(cmd)
reb = curs.fetchall()

cmd = "SELECT teams.abrv, AVG(teamStats.pts) FROM teams, teamStats, games WHERE teams.teamId = teamStats.oppId AND games.gameId = teamStats.gameId AND games.season = 2018 GROUP BY teams.teamId"
curs.execute(cmd)
opp = curs.fetchall()

conn.close()


plt.bar([i for i in range(len(reb))], [reb[i][1] - opp[i][1] for i in range(len(reb))])
plt.xticks([i for i in range(len(reb))], [x[0] for x in reb])

plt.show()
