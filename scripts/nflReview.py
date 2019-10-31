import NFLProjections.NFLProjections.DB.NFL as DB
from matplotlib import pyplot as plt
from pprint import pprint
import numpy
import scipy.stats as sci




def getGDCmd(startDate=None, endDate=None, season=None, gameId=None):
    gameDateCmd = """
                SELECT game_id, home_id, away_id
                    FROM games
                    {}
                """
    whereCmd = ""
##    print(startDate)
    if season:
        whereCmd = "WHERE season = {}".format(season)
    elif gameId:
        whereCmd = "WHERE game_id > {} AND game_type = 'Regular Season'".format(gameId)
    elif not startDate and not endDate:
        pass
    elif not endDate:
        whereCmd = "WHERE season = {} AND game_date >= {}.{}".format(*str(startDate).split("-"))
    elif not startDate:
        whereCmd = "WHERE game_date <= {}.{}".format(*str(endDate).split("-")[1:])
    else:
        whereCmd = "WHERE game_date >= {}.{} AND game_date <= {}.{}".format(*str(startDate).split("-")[1:], *str(endDate).split("-")[1:])
    return gameDateCmd.format(whereCmd)


def setScoreCmd(multiply, stat):
    scoreCmd = """
            SELECT game_id, team_id, opp_id, player_id, value * {0[multiply]} AS score
                FROM player_stats
                WHERE stat_id = {0[stat]}{0[andPlayerCmd]}
            """
    return scoreCmd.format({"multiply": multiply, "stat": stat, "andPlayerCmd":"{0[andPlayerCmd]}"})


def setTScoreCmd(multiply, stat, thresh):
    scoreCmd = """
                SELECT game_id, team_id, opp_id, player_id, (CASE WHEN value >= {0[threshold]} THEN {0[multiply]} ELSE 0 END) AS score
                FROM player_stats
                WHERE stat_id = {0[stat]}{0[andPlayerCmd]}
            """
    return scoreCmd.format({"multiply": multiply, "stat": stat, "threshold": thresh, "andPlayerCmd":"{0[andPlayerCmd]}"})



def setValueCmd(stat):
    valueCmd = """
            SELECT game_id, team_id, opp_id, player_id, value
                FROM player_stats
                WHERE stat_id = {0[stat]}{0[andPlayerCmd]}
            """
    return valueCmd.format({"stat": stat, "andPlayerCmd":"{0[andPlayerCmd]}"})


paTdScore = setScoreCmd(4, 108)
paYdScore = setScoreCmd(.04, 105)
pa300Score = setTScoreCmd(3, 105, 300)
paIntScore = setScoreCmd(-1, 109)

ruTdScore = setScoreCmd(6, 207)
ruYdScore = setScoreCmd(.1, 203)
ru100Score = setTScoreCmd(3, 203, 100)
fumScore = setScoreCmd(-1, 3)

recScore = setScoreCmd(1, 302)
recTdScore = setScoreCmd(6, 309)
recYdScore = setScoreCmd(.1, 303)
rec100Score = setTScoreCmd(3, 203, 100)





passScoreCmd = """
                SELECT td.game_id, td.team_id, td.opp_id, td.player_id, (td.score + yds.score + thresh.score + ints.score) AS score
                    FROM ( {0[tdCmd]} ) AS td
                    INNER JOIN ( {0[ydsCmd]} ) AS yds
                        ON td.game_id = yds.game_id AND td.player_id = yds.player_id
                    INNER JOIN ( {0[threshCmd]} ) AS thresh
                        ON td.game_id = thresh.game_id AND td.player_id = thresh.player_id
                    INNER JOIN ( {0[intsCmd]} ) AS ints
                        ON td.game_id = ints.game_id AND td.player_id = ints.player_id
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON td.game_id = gd.game_id
                """.format({"tdCmd": paTdScore, "ydsCmd": paYdScore, "threshCmd": pa300Score, "intsCmd": paIntScore, "gdCmd": "{0[gdCmd]}"})

rushScoreCmd = """
                SELECT td.game_id, td.team_id, td.opp_id, td.player_id, (td.score + yds.score + thresh.score + fum.score) AS score
                    FROM ( {0[tdCmd]} ) AS td
                    INNER JOIN ( {0[ydsCmd]} ) AS yds
                        ON td.game_id = yds.game_id AND td.player_id = yds.player_id
                    INNER JOIN ( {0[threshCmd]} ) AS thresh
                        ON td.game_id = thresh.game_id AND td.player_id = thresh.player_id
                    INNER JOIN ( {0[fumCmd]} ) AS fum
                        ON td.game_id = fum.game_id AND td.player_id = fum.player_id
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON td.game_id = gd.game_id
                """.format({"tdCmd": ruTdScore, "ydsCmd": ruYdScore, "threshCmd": ru100Score, "fumCmd": fumScore, "gdCmd": "{0[gdCmd]}"})

recScoreCmd = """
                SELECT td.game_id, td.team_id, td.opp_id, td.player_id, (td.score + yds.score + thresh.score + rec.score) AS score
                    FROM ( {0[tdCmd]} ) AS td
                    INNER JOIN ( {0[ydsCmd]} ) AS yds
                        ON td.game_id = yds.game_id AND td.player_id = yds.player_id
                    INNER JOIN ( {0[threshCmd]} ) AS thresh
                        ON td.game_id = thresh.game_id AND td.player_id = thresh.player_id
                    INNER JOIN ( {0[recCmd]} ) AS rec
                        ON td.game_id = rec.game_id AND td.player_id = rec.player_id
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON td.game_id = gd.game_id
                """.format({"tdCmd": recTdScore, "ydsCmd": recYdScore, "threshCmd": rec100Score, "recCmd": recScore, "gdCmd": "{0[gdCmd]}"})


offScoreCmd = """
                SELECT pass.game_id,
                        pass.player_id,
                        pass.team_id,
                        pass.opp_id,
                        (pass.score + rush.score + rec.score) AS total
                    FROM ( {0[passScoreCmd]} ) AS pass
                    INNER JOIN ( {0[rushScoreCmd]} ) AS rush
                        ON pass.player_id = rush.player_id AND pass.game_id = rush.game_id
                    INNER JOIN ( {0[recScoreCmd]} ) AS rec
                        ON pass.player_id = rec.player_id AND pass.game_id = rec.game_id
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON pass.game_id = gd.game_id
                    INNER JOIN pro_players AS pp
                        ON pass.player_id = pp.player_id
                    {0[whrPlayerCmd]}
            
            """.format({"passScoreCmd":passScoreCmd, "rushScoreCmd":rushScoreCmd, "recScoreCmd":recScoreCmd,
                        "gdCmd":"{0[gdCmd]}", "whrPlayerCmd": "{0[whrPlayerCmd]}"})



offAvgScoreCmd = """
                    SELECT abrv, COUNT(off.game_id), AVG(total)
                        FROM ( {0[offCmd]} ) AS off
                        INNER JOIN pro_players AS pp
                            ON off.player_id = pp.player_id
                        INNER JOIN pro_teams AS opp
                            ON off.opp_id = opp.team_id
                        {0[whrCmd]}
                        GROUP BY off.opp_id
                        ORDER BY AVG(total) DESC
                """.format({"offCmd": offScoreCmd, "whrCmd": "{0[whrCmd]}"})
 











            
                


nflDB = DB.NFLDatabase()
nflDB.openDB()


        
        
pprint(nflDB.fetchAll(offAvgScoreCmd.format({"whrCmd": "", "whrPlayerCmd":" WHERE pos_id = 9", "andPlayerCmd":"", "gdCmd":getGDCmd(gameId=20180910013)}) )) 


  




nflDB.closeDB()







    
