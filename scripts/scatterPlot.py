import NFLProjections.NFLProjections.DB.NFL as DB
from matplotlib import pyplot as plt
from pprint import pprint
import numpy
import scipy.stats as sci


firstWins = """
                SELECT value
                    FROM team_stats
                    INNER JOIN stat_types
                        ON team_stats.stat_id = stat_types.stat_id
                    INNER JOIN games
                        ON team_stats.game_id = games.game_id
                    WHERE abrv = 'Points'
                    GROUP BY season)
            """

teamWins = """
                SELECT season, team_id, COUNT(winner_id) AS wins
                    FROM games
                    INNER JOIN pro_teams
                        ON games.winner_id = pro_teams.team_id
                    WHERE game_type = 'Regular Season'
                    GROUP BY team_id, season
            """


teamPts = """
                SELECT season, team_id, SUM(value) AS points
                    FROM team_stats
                    INNER JOIN games
                        ON games.game_id = team_stats.game_id
                    INNER JOIN stat_types
                        ON team_stats.stat_id = stat_types.stat_id                    
                    WHERE game_type = 'Regular Season' AND abrv = 'Pts'
                    GROUP BY team_id, season
            """

thirdEff = """
            SELECT season, team_id, (CASE WHEN team_stats.team_id = games.winner_id THEN 1 ELSE 0 END), value
                FROM team_stats
                INNER JOIN games
                    On team_stats.game_id = games.game_id
                INNER JOIN stat_types
                    ON team_stats.stat_id = stat_types.stat_id
                WHERE game_type = 'Regular Season' AND abrv = '4DE'
            """


puntRYds = """
            SELECT season, opp_id AS team_id, SUM(value) AS value
                FROM player_stats
                INNER JOIN games
                    ON player_stats.game_id = games.game_id
                INNER JOIN stat_types
                    ON player_stats.stat_id = stat_types.stat_id
                WHERE game_type = 'Regular Season' AND abrv = 'Sack'
                GROUP BY opp_id, season
        """


punts = """
            SELECT season, team_id, SUM(value) AS value
                FROM player_stats
                INNER JOIN games
                    ON player_stats.game_id = games.game_id
                INNER JOIN stat_types
                    ON player_stats.stat_id = stat_types.stat_id
                WHERE game_type = 'Regular Season' AND abrv = 'KR'
                GROUP BY team_id, season
        """



teamPtsWins = """
                SELECT a.wins, b.value
                    FROM (
                        {}
                        ) AS a
                    INNER JOIN (
                        {}
                        ) AS b
                        ON a.season = b.season AND a.team_id = b.team_id
                    
                """.format(teamWins, puntRYds)


teamYds = """
            SELECT abrv, SUM(value)
                FROM player_stats
                INNER JOIN pro_teams
                    ON player_stats.team_id = pro_teams.team_id
                INNER JOIN games
                    ON player_stats.game_id = games.game_id
                WHERE stat_id = 111 AND season = 2018 AND conference = ? AND division = ?
                GROUP BY pro_teams.team_id
            """
            
                


def fixRatio(item):
    x,y = [int(x) for x in str(item).split(".")]
    if x > y:
        y *= 10
    return (x,y)


nflDB = DB.NFLDatabase()
nflDB.openDB()

for conf in ("AFC", "NFC"):
    for divi in ("East", "South", "West", "North"):
        X,Y = zip(*nflDB.fetchAll(teamYds,(conf,divi)))
        plt.bar(numpy.arange(len(X)),Y)
        plt.xticks(numpy.arange(len(X)),X)
        plt.show()
        
        



X,Y = zip(*nflDB.fetchAll(teamPtsWins))
##X = [stat[-2]/stat[-1] for stat in stats if stat[-1] !=0]
##Y = [stat[-3] for stat in stats if stat[-1] != 0]
print(numpy.corrcoef(X,Y))



##fd = numpy.array([x[0] for x in nflDB.fetchAll(firstWins)])
##mean = numpy.mean(fd)
##demean = mean - fd[:numpy.newaxis]
##std = numpy.std(fd)
##destd = numpy.std(demean)
##
##pprint(numpy.histogram(fd))

plt.scatter(X,Y)
plt.show()
    




nflDB.closeDB()







    
