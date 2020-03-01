import datetime

from pprint import pprint
from json import load
from itertools import chain

import numpy
import matplotlib.pyplot as plt

today = datetime.date.today()


def yId(yahooId):
    return yahooId.split(".")[-1]

def formGDCmd(season=None, startDate=None, endDate=today):
    cmd = None
    baseCmd = "SELECT game_id, season, game_date, home_id, away_id, winner_id, loser_id FROM games {0[whrCmd]}"
    whrCmd = "WHERE game_type = 'season' AND season = "+str(season)+" {0[andCmd]}"
    if not season:
        cmd = baseCmd.format({"whrCmd":"WHERE game_type = 'season'"})
    elif not startDate:
        andCmd = ""
        where = whrCmd.format({"andCmd": ""})
        cmd = baseCmd.format({"whrCmd":where})
    else:
        startMonth, startDay = str(startDate).split("-")[1:]
        endMonth, endDay = str(endDate).split("-")[1:]

        if startDate.year != endDate.year:
            andCmd = "AND (game_date >= {}.{} OR game_date <= {}.{})".format(startMonth, startDay, endMonth, endDay)
        else:
            andCmd = "AND game_date >= {}.{} AND year = {}".format(startMonth, startDay, startDate.year)
        where = whrCmd.format({"andCmd": andCmd})
        cmd = baseCmd.format({"whrCmd":where})
    return cmd



twoWeeks = today - datetime.timedelta(14)
oneMonth = today - datetime.timedelta(30)
sixWeeks = today - datetime.timedelta(42)
threeMonths = today - datetime.timedelta(90)

allCmd = formGDCmd()
seasonCmd = formGDCmd(2019)
twoWeeksCmd = formGDCmd(2019, twoWeeks)
oneMonthCmd = formGDCmd(2019, oneMonth)
sixWeeksCmd = formGDCmd(2019, sixWeeks)
threeMonthsCmd = formGDCmd(2019, threeMonths)


dkScoreCmd = """
                SELECT gd.game_id, ps.team_id, ps.opp_id,
                        ps.player_id, mins,
                        (pts + tpm*.5 + reb*1.25 + ast*1.5 + stl*2 + blk*2 +trn*-.5 +
                            (CASE WHEN pts >= 10 AND reb >= 10 THEN 1.5
                                    WHEN pts >= 10 AND ast >= 10 THEN 1.5
                                    WHEN reb >= 10 AND ast >= 10 THEN 1.5
                                    ELSE 0 END) +
                            (CASE WHEN pts >= 10 AND reb >= 10 AND ast >= 10 THEN 3 ELSE 0 END)) AS score
                    FROM player_stats AS ps
                    INNER JOIN ({0[gdCmd]}) AS gd
                        ON ps.game_id = gd.game_id
                    {0[scoreWhereCmd]}
            """

b2bCmd = """
            SELECT game_id
                FROM games
                WHERE year = ? AND game_date = ? AND (home_id = ? OR away_id = ?)
        """




newPlayersCmd = """
                    SELECT DISTINCT player_id
                        FROM player_stats AS ps
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ps.game_id = gd.game_id
                        WHERE player_id NOT IN (SELECT player_id FROM pro_players)
                """


gameOddsCmd = """
                SELECT away.spread, away.money, away.spread_outcome, away.money_outcome,
                        home.spread, home.money, home.spread_outcome, home.money_outcome,
                        ou, ov.outcome
                    FROM games AS g
                    INNER JOIN game_lines AS away
                        ON g.game_id = away.game_id AND g.away_id = away.team_id
                    INNER JOIN game_lines AS home
                        ON g.game_id = home.game_id AND g.home_id = home.team_id
                    INNER JOIN over_unders AS ov
                        ON g.game_id = ov.game_id
                    WHERE g.game_id = ?
                """


teamGameStats = """
                    SELECT b2b, fga, fgm, fta, ftm, tpa, tpm, pts, oreb, dreb, reb, ast, stl, blk, trn, fls
                        FROM team_stats
                        WHERE game_id = ? AND team_id = ?
                """


colGameStats = """
                    SELECT fga, fgm, fta, ftm, tpa, tpm, pts, oreb, dreb, reb, ast, stl, blk, trn, fls
                        FROM team_stats
                        WHERE game_id = ? AND team_id = ?
                """


winCmd = """
            SELECT team_id, COUNT(gl.game_id) AS wins
                FROM game_lines AS gl
                INNER JOIN ( {0[gdCmd]} ) AS gd
                    ON gl.game_id = gd.game_id
                WHERE money_outcome = 1
                GROUP BY team_id
        """


loseCmd = """
            SELECT team_id, COUNT(gl.game_id) AS loses
                FROM game_lines AS gl
                INNER JOIN ( {0[gdCmd]} ) AS gd
                    ON gl.game_id = gd.game_id
                WHERE money_outcome = -1
                GROUP BY team_id
        """


atsWins = """
            SELECT team_id, COUNT(gl.game_id) AS wins
                FROM game_lines AS gl
                INNER JOIN ( {0[gdCmd]} ) AS gd
                    ON gl.game_id = gd.game_id
                WHERE spread_outcome = 1
                GROUP BY team_id
        """


atsLoses = """
            SELECT team_id, COUNT(gl.game_id) AS loses
                FROM game_lines AS gl
                INNER JOIN ( {0[gdCmd]} ) AS gd
                    ON gl.game_id = gd.game_id
                WHERE spread_outcome = -1
                GROUP BY team_id
        """


teamResultStats = """
                    SELECT (CASE WHEN wins.wins IS NULL THEN 0 ELSE wins.wins END),
                            (CASE WHEN loses.loses IS NULL THEN 0 ELSE loses.loses END),
                            (CASE WHEN ats_wins.wins IS NULL THEN 0 ELSE ats_wins.wins END),
                            (CASE WHEN ats_loses.loses IS NULL THEN 0 ELSE ats_loses.loses END),
                            AVG(total), AVG(money), AVG(spread), AVG(result)
                        FROM team_stats AS ts
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ts.game_id = gd.game_id {0[andJoinGD]}
                        INNER JOIN game_lines AS gl
                            ON ts.game_id = gl.game_id AND ts.team_id = gl.team_id
                        LEFT JOIN ( {0[winCmd]} ) AS wins
                            ON ts.team_id = wins.team_id
                        LEFT JOIN ( {0[loseCmd]} ) AS loses
                            ON ts.team_id = loses.team_id
                        LEFT JOIN ( {0[atsWins]} ) AS ats_wins
                            ON ts.team_id = ats_wins.team_id
                        LEFT JOIN ( {0[atsLoses]} ) AS ats_loses
                            ON ts.team_id = ats_loses.team_id
                        INNER JOIN over_unders AS ov
                            ON ts.game_id = ov.game_id
                        WHERE ts.team_id = ?
                        GROUP BY ts.team_id
                    """.format({"gdCmd": "{0[gdCmd]}", "winCmd": winCmd, "loseCmd":loseCmd,
                                "atsWins": atsWins, "atsLoses": atsLoses, "andJoinGD": "{0[andJoinGD]}"})


teamAvgStats = """
                    SELECT SUM(b2b), AVG(fga), AVG(fgm),
                            AVG(fta), AVG(ftm), AVG(tpa), AVG(tpm), AVG(pts), AVG(oreb),
                            AVG(dreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn), AVG(fls)
                        FROM team_stats AS ts
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ts.game_id = gd.game_id {0[andJoinGD]}
                        WHERE ts.{0[team]}_id = ?
                        GROUP BY ts.{0[team]}_id
                """


colTeamAvgStats = """
                    SELECT AVG(fga), AVG(fgm),
                            AVG(fta), AVG(ftm), AVG(tpa), AVG(tpm), AVG(pts), AVG(oreb),
                            AVG(dreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn), AVG(fls)
                        FROM team_stats AS ts
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ts.game_id = gd.game_id {0[andJoinGD]}
                        WHERE ts.{0[team]}_id = ?
                        GROUP BY ts.{0[team]}_id
                """


leagueAvgStats = """
                    SELECT AVG(fga), AVG(fgm),
                            AVG(fta), AVG(ftm), AVG(tpa), AVG(tpm), AVG(pts), AVG(oreb),
                            AVG(dreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn), AVG(fls)
                        FROM team_stats AS ts
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ts.game_id = gd.game_id {0[andJoinGD]}
                """


playerGameStats = """
                    SELECT ps.player_id, ps.mins, fga, fgm, fta, ftm, tpa, tpm, pts, reb,
                            ast, stl, blk, trn, fls, score
                        FROM player_stats AS ps
                        INNER JOIN ( {} ) AS sc
                            ON ps.game_id = sc.game_id AND ps.player_id = sc.player_id
                        ORDER BY score DESC
                    """.format(dkScoreCmd)


playerAvgStats = """
                    SELECT AVG(ps.mins), AVG(fga), AVG(fgm), AVG(fta), AVG(ftm),
                            AVG(tpa), AVG(tpm), AVG(pts), AVG(reb), AVG(ast), AVG(stl),
                            AVG(blk), AVG(trn), AVG(fls), AVG(score)
                        FROM player_stats AS ps
                        INNER JOIN ( {} ) AS sc
                            ON ps.game_id = sc.game_id AND ps.player_id = sc.player_id
                    """.format(dkScoreCmd)


gameShotStats = """
                SELECT COUNT(player_shot_id), SUM(made), SUM(pts)
                    FROM player_shots AS ps
                    WHERE game_id = ? AND team_id = ? AND box = ?
                """


teamShotStats = """
                SELECT COUNT(player_shot_id)/COUNT(DISTINCT ps.game_id)*1.0, SUM(made)*1.0/COUNT(DISTINCT ps.game_id), SUM(pts)*1.0/COUNT(DISTINCT ps.game_id)
                    FROM player_shots AS ps
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON ps.game_id = gd.game_id
                    WHERE ps.{0[team]}_id = ? AND box = ?
                """


spreadResultCmd = """
                    SELECT game_date, (CASE WHEN gl.team_id = home_id THEN home_id ELSE away_id END),
                            (CASE WHEN gl.team_id = games.home_id THEN 1 ELSE 0 END),
                            (CASE WHEN gl.team_id != home_id THEN home_id ELSE away_id END),
                            spread, result, ou, total, money
                        FROM game_lines AS gl
                        INNER JOIN games
                            ON gl.game_id = games.game_id
                        INNER JOIN over_unders AS ov
                            ON gl.game_id = ov.game_id
                        WHERE season = 2019 AND gl.team_id = ?
                        ORDER BY gl.game_id DESC
                """
