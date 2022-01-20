import datetime

from pprint import pprint
from json import load
from itertools import chain

import numpy
import matplotlib.pyplot as plt

today = datetime.date.today()

##################
currentSeason = 2020
#####################

def yId(yahooId):
    return yahooId.split(".")[-1]

def formGDCmd(season=None, startDate=None, endDate=today, gameId=None):
    endMonth, endDay = str(endDate).split("-")[1:]
    cmd = None
    baseCmd = "SELECT game_id, game_date, home_id, away_id, winner_id, loser_id FROM games {0[whrCmd]}"
    whrCmd = "WHERE season = "+str(season)+" {0[andCmd]}"
    if not season:
        cmd = baseCmd.format({"whrCmd":""})
    elif not startDate:
        andCmd = ""
        if gameId:
            where = whrCmd.format({"andCmd": "AND game_id < {}".format(gameId)})
        else:
            where = whrCmd.format({"andCmd": ""})
        cmd = baseCmd.format({"whrCmd":where})
    else:
        startMonth, startDay = str(startDate).split("-")[1:]

        if startDate.year != endDate.year:
            andCmd = "AND ((game_date >= {}.{} AND game_year = {}) OR (game_date <= {}.{} AND game_year = {}))".format(startMonth, startDay, startDate.year, endMonth, endDay, endDate.year)
        else:
            andCmd = "AND game_date >= {}.{} AND game_date < {}.{} AND game_year = {}".format(startMonth, startDay, endMonth, endDay, startDate.year)
        where = whrCmd.format({"andCmd": andCmd})
        cmd = baseCmd.format({"whrCmd":where})
    return cmd



twoWeeks = today - datetime.timedelta(14)
oneMonth = today - datetime.timedelta(30)
twoMonths = today - datetime.timedelta(60)


def getGDCmds(currentSeason):
    cmds = {}
    cmds["All"] = formGDCmd()
    cmds["Season"] = formGDCmd(int(currentSeason))
    cmds["PrvSeason"] = formGDCmd(int(currentSeason)-1)
    cmds["1Month"] = formGDCmd(int(currentSeason), oneMonth)
    cmds["2Weeks"] = formGDCmd(int(currentSeason), twoWeeks)
    cmds["2Months"] = formGDCmd(currentSeason, twoMonths)
    return cmds.copy()

## ---------------------------------------------


andGDCmd = "AND team.team_id = gd.{}_id"


atsCmd = """
            SELECT IFNULL(wins.total, 0), IFNULL(loses.total, 0), IFNULL(ties.total,0)

                FROM teams

                LEFT JOIN (
                            SELECT gl.team_id, COUNT(gl.game_id) AS total
                                FROM game_lines AS gl
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON gl.game_id = gd.game_id
                                WHERE spread_outcome = 1
                                GROUP BY gl.team_id
                            ) AS wins
                    ON teams.team_id = wins.team_id

                LEFT JOIN (
                            SELECT gl.team_id, COUNT(gl.game_id) AS total
                                FROM game_lines AS gl
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON gl.game_id = gd.game_id
                                WHERE spread_outcome = -1
                                GROUP BY gl.team_id
                            ) AS loses
                    ON teams.team_id = loses.team_id

                LEFT JOIN (
                            SELECT gl.team_id, COUNT(gl.game_id) AS total
                                FROM game_lines AS gl
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON gl.game_id = gd.game_id
                                WHERE spread_outcome = 0
                                GROUP BY gl.team_id
                            ) AS ties
                    ON teams.team_id = ties.team_id

                WHERE teams.team_id = ?
        """


batResultCmd = """
                    SELECT COUNT(ab_results.batter_id), (IFNULL(hits.total, 0)*1.0)/(COUNT(ab_results.pitcher_id)-bb.total), (IFNULL(k.total, 0)*100.0)/(COUNT(ab_results.pitcher_id)), (IFNULL(hrs.total,0)*100.0)/(COUNT(ab_results.pitcher_id)), (IFNULL(bb.total,0)*100.0)/COUNT(ab_results.pitcher_id)
                        FROM ab_results
                        INNER JOIN players
                            ON ab_results.pitcher_id = players.player_id
                        INNER JOIN pitches
                            ON ab_results.pitch_id = pitches.pitch_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ab_results.game_id = gd.game_id
                        LEFT JOIN ( SELECT ab_results.batter_id, COUNT(ab_results.batter_id) AS total
                                        FROM ab_results
                                        INNER JOIN pitches
                                            ON ab_results.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab_results.game_id = gd.game_id
                                        INNER JOIN players
                                            ON ab_results.pitcher_id = players.player_id
                                        WHERE throws = '{0[throws]}' AND ab_type_id IN (2,6,8,15)
                                        GROUP BY ab_results.batter_id
                                    ) AS hits
                            ON ab_results.batter_id = hits.batter_id

                        LEFT JOIN ( SELECT ab_results.batter_id, COUNT(ab_results.batter_id) AS total
                                        FROM ab_results
                                        INNER JOIN pitches
                                            ON ab_results.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab_results.game_id = gd.game_id
                                        INNER JOIN players
                                            ON ab_results.pitcher_id = players.player_id
                                        WHERE throws = '{0[throws]}' AND ab_type_id = 8
                                        GROUP BY ab_results.batter_id
                                    ) AS hrs
                            ON ab_results.batter_id = hrs.batter_id

                        LEFT JOIN ( SELECT ab_results.batter_id, COUNT(ab_results.batter_id) AS total
                                        FROM ab_results
                                        INNER JOIN pitches
                                            ON ab_results.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab_results.game_id = gd.game_id
                                        INNER JOIN players
                                            ON ab_results.pitcher_id = players.player_id
                                        WHERE throws = '{0[throws]}' AND ab_type_id = 1
                                        GROUP BY ab_results.batter_id
                                    ) AS k
                            ON ab_results.batter_id = k.batter_id

                        LEFT JOIN ( SELECT ab_results.batter_id, COUNT(ab_results.batter_id) AS total
                                        FROM ab_results
                                        INNER JOIN pitches
                                            ON ab_results.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab_results.game_id = gd.game_id
                                        INNER JOIN players
                                            ON ab_results.pitcher_id = players.player_id
                                        WHERE throws = '{0[throws]}' AND ab_type_id = 4
                                        GROUP BY ab_results.batter_id
                                    ) AS bb
                            ON ab_results.batter_id = bb.batter_id

                        WHERE ab_results.batter_id = ? AND throws = '{0[throws]}'
                """


vsResultCmd = """
                    SELECT COUNT(ab.batter_id), (IFNULL(hits.total, 0)*1.0)/(COUNT(ab.pitcher_id)-bb.total), (IFNULL(k.total, 0)*100.0)/(COUNT(ab.pitcher_id)), (IFNULL(hrs.total,0)*100.0)/(COUNT(ab.pitcher_id)), (IFNULL(bb.total,0)*100.0)/COUNT(ab.pitcher_id)
                        FROM ab_results AS ab
                        INNER JOIN pitches
                            ON ab.pitch_id = pitches.pitch_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ab.game_id = gd.game_id
                        LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                        FROM ab_results AS ab
                                        INNER JOIN pitches
                                            ON ab.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab.game_id = gd.game_id
                                        WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id IN (2,6,8,15)
                                        GROUP BY ab.batter_id
                                    ) AS hits
                            ON ab.batter_id = hits.batter_id

                        LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                        FROM ab_results AS ab
                                        INNER JOIN pitches
                                            ON ab.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab.game_id = gd.game_id
                                        WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 8
                                        GROUP BY ab.batter_id
                                    ) AS hrs
                            ON ab.batter_id = hrs.batter_id

                        LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                        FROM ab_results AS ab
                                        INNER JOIN pitches
                                            ON ab.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab.game_id = gd.game_id
                                        WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 1
                                        GROUP BY ab.batter_id
                                    ) AS k
                            ON ab.batter_id = k.batter_id

                        LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                        FROM ab_results AS ab
                                        INNER JOIN pitches
                                            ON ab.pitch_id = pitches.pitch_id
                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON ab.game_id = gd.game_id
                                        WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 4
                                        GROUP BY ab.batter_id
                                    ) AS bb
                            ON ab.batter_id = bb.batter_id

                        WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]}
                """


batterStats = """
                SELECT SUM(ab), SUM(h)*1.0/SUM(ab), SUM(r), SUM(hr), SUM(rbi), SUM(sb), (((SUM(bb)+SUM(h))*1.0)/(SUM(ab)+SUM(bb))) + (((SUM(h)+SUM(dbl)+(SUM(tpl)*2)+(SUM(hr)*3))*1.0))/SUM(ab)
                    FROM batter_stats AS bs
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON bs.game_id = gd.game_id
                    WHERE player_id = ?
            """


bullpenCmd = """
                SELECT DISTINCT players.player_id
                    FROM players
                    INNER JOIN bullpens
                        ON players.player_id = bullpens.player_id
                    INNER JOIN ( SELECT game_id
                                    FROM games
                                    INNER JOIN teams
                                        ON games.home_id = teams.team_id OR games.away_id = teams.team_id
                                    WHERE team_id = ?
                                    ORDER BY game_id DESC
                                    LIMIT 10
                                ) AS gd
                        ON bullpens.game_id = gd.game_id
                    WHERE pitch_order > 1
            """



b2bCmd = """
            SELECT ts.game_id
                FROM games
                INNER JOIN team_stats AS ts
                    ON games.game_id = ts.game_id
                WHERE game_year = ? AND game_date = ? AND team_id = ?
        """


commonOppCmd = """
                SELECT team_id, abrv, first_name, last_name
                    FROM teams
                    INNER JOIN (SELECT DISTINCT opp_id AS opp_id
                                    FROM team_stats AS ts
                                    INNER JOIN ( {0[gdCmd]} ) AS gd
                                        ON ts.game_id = gd.game_id
                                        WHERE team_id = ? ) AS away
                        ON teams.team_id = away.opp_id
                    INNER JOIN (SELECT DISTINCT opp_id AS opp_id
                                    FROM team_stats AS ts
                                    INNER JOIN ( {0[gdCmd]} ) AS gd
                                        ON ts.game_id = gd.game_id
                                        WHERE team_id = ? ) AS home
                        ON away.opp_id = home.opp_id
                """


distinctPlayerCmd = """
                    SELECT DISTINCT player_id
                        FROM player_stats
                        WHERE player_id NOT IN (SELECT player_id FROM players)
                    """


distinctBatterCmd = """
                    SELECT DISTINCT player_id
                        FROM batter_stats
                        WHERE player_id NOT IN (SELECT player_id FROM players)
                    """

distinctPitcherCmd = """
                    SELECT DISTINCT player_id
                        FROM pitcher_stats
                        WHERE player_id NOT IN (SELECT player_id FROM players)
                    """



gameLineCmd = """
                SELECT game_time, (CASE WHEN gl.team_id = gd.home_id THEN 1 ELSE 0 END), team_id, opp_id, spread, result, money, spread_outcome,
                        money_outcome, ou, total, outcome
                    FROM game_lines AS gl
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON gl.game_id = gd.game_id
                    INNER JOIN over_unders AS ov
                        ON gl.game_id = ov.game_id
                    WHERE team_id = ?
                """


gamesCmd = """
            SELECT games.game_id, season, game_year, game_date, away_id, home_id, spread, result, ou, total
                FROM games
                INNER JOIN game_lines AS gl
                    ON games.game_id = gl.game_id AND games.home_id = gl.team_id
                INNER JOIN over_unders AS ov
                    ON games.game_id = ov.game_id
                WHERE game_type = 'season'
                ORDER BY games.game_id
           """


groupAtsCmd = """
                SELECT teams.first_name || " " || teams.last_name, SUM((CASE spread_outcome WHEN 1 THEN 1 ELSE 0 END)) AS wins,
                        SUM((CASE spread_outcome WHEN -1 THEN 1 ELSE 0 END)) AS loses, SUM((CASE spread_outcome WHEN 0 THEN 1 ELSE 0 END)) AS push,
                        AVG(spread), AVG(result)
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN teams
                        ON gd.home_id = teams.team_id OR gd.away_id = teams.team_id
                    INNER JOIN game_lines AS gl
                        ON gd.game_id = gl.game_id AND teams.team_id = gl.team_id
                    GROUP BY teams.team_id

                """


groupNBATeamStatsCmd = """
                    SELECT team.team_id, COUNT(team.game_id), AVG(team.pts), AVG(team.fgm), AVG(team.ftm), AVG(team.tpm),
                            SUM(team.fgm)/(SUM(team.fga)*1.0), SUM(team.ftm)/(SUM(team.fta)*1.0),
                            SUM(team.tpm)/(SUM(team.tpa)*1.0), AVG(team.oreb), AVG(team.dreb), AVG(team.reb), AVG(team.ast), AVG(team.stl),
                            AVG(team.blk), AVG(team.trn), AVG(team.fls), AVG(team.pts_in_pt), AVG(team.fb_pts),
                            COUNT(opp.game_id), AVG(opp.pts), AVG(opp.fgm), AVG(opp.ftm), AVG(opp.tpm),
                            SUM(opp.fgm)/(SUM(opp.fga)*1.0), SUM(opp.ftm)/(SUM(opp.fta)*1.0),
                            SUM(opp.tpm)/(SUM(opp.tpa)*1.0), AVG(opp.oreb), AVG(opp.dreb), AVG(opp.reb), AVG(opp.ast), AVG(opp.stl),
                            AVG(opp.blk), AVG(opp.trn), AVG(opp.fls), AVG(opp.pts_in_pt), AVG(opp.fb_pts)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id {0[andGDCmd]}
                        GROUP BY team.team_id
                    """


groupNCAABTeamStatsCmd = """
                    SELECT team.team_id, COUNT(team.game_id), AVG(team.pts), AVG(team.fgm), AVG(team.ftm), AVG(team.tpm),
                            SUM(team.fgm)/(SUM(team.fga)*1.0), SUM(team.ftm)/(SUM(team.fta)*1.0),
                            SUM(team.tpm)/(SUM(team.tpa)*1.0), AVG(team.oreb), AVG(team.dreb), AVG(team.reb), AVG(team.ast), AVG(team.stl),
                            AVG(team.blk), AVG(team.trn), AVG(team.fls),
                            COUNT(opp.game_id), AVG(opp.pts), AVG(opp.fgm), AVG(opp.ftm), AVG(opp.tpm),
                            SUM(opp.fgm)/(SUM(opp.fga)*1.0), SUM(opp.ftm)/(SUM(opp.fta)*1.0),
                            SUM(opp.tpm)/(SUM(opp.tpa)*1.0), AVG(opp.oreb), AVG(opp.dreb), AVG(opp.reb), AVG(opp.ast), AVG(opp.stl),
                            AVG(opp.blk), AVG(opp.trn), AVG(opp.fls)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id {0[andGDCmd]}
                        GROUP BY team.team_id
                    """


groupOuCmd = """
                SELECT teams.first_name || " " || teams.last_name, SUM((CASE outcome WHEN 1 THEN 1 ELSE 0 END)) AS wins,
                        SUM((CASE outcome WHEN -1 THEN 1 ELSE 0 END)) AS loses, SUM((CASE outcome WHEN 0 THEN 1 ELSE 0 END)) AS push,
                        AVG(ou), AVG(total)
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN teams
                        ON gd.home_id = teams.team_id OR gd.away_id = teams.team_id
                    INNER JOIN over_unders AS ov
                        ON gd.game_id = ov.game_id
                    GROUP BY teams.team_id


            """


groupRecordCmd = """
                    SELECT teams.first_name || " " || teams.last_name, SUM((CASE WHEN gd.winner_id = teams.team_id THEN 1 ELSE 0 END)) AS wins, SUM((CASE WHEN gd.loser_id = teams.team_id THEN 1 ELSE 0 END)) AS loses
                        FROM ( {0[gdCmd]} ) AS gd
                        INNER JOIN teams
                            ON gd.home_id = teams.team_id OR gd.away_id = teams.team_id
                        GROUP BY teams.team_id
                """


lineupCmd = """
                SELECT player_id
                    FROM lineups
                    INNER JOIN (
                                SELECT game_id, team_id
                                    FROM games
                                    INNER JOIN teams
                                        ON games.home_id = teams.team_id OR games.away_id = teams.team_id
                                    WHERE team_id = ?
                                    ORDER BY game_id DESC
                                    LIMIT 1
                                ) AS gd
                        ON lineups.game_id = gd.game_id AND lineups.team_id = gd.team_id
                    WHERE batt_order <= 9 AND sub_order = 1
                    ORDER BY batt_order
            """


mlbTeamStatsCmd = """
                    SELECT COUNT(team.game_id), AVG(team.ab), (SUM(team.h)*1.0)/SUM(team.ab), AVG(team.r),
                            AVG(team.hr), AVG(team.so), AVG(team.lob), AVG(team.ip), AVG(team.ra),
                            (SUM(team.er)*9.0)/SUM(team.ip), AVG(team.k), AVG(team.hra),
                            COUNT(opp.game_id), AVG(opp.ab), (SUM(opp.h)*1.0)/SUM(opp.ab), AVG(opp.r),
                            AVG(opp.hr), AVG(opp.so), AVG(opp.lob), AVG(opp.ip), AVG(opp.ra),
                            (SUM(opp.er)*9.0)/SUM(opp.ip), AVG(opp.k), AVG(opp.hra)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id {0[andGDCmd]}
                        WHERE team.team_id = ?
                    """

mlbOppStatsCmd = """
                    SELECT COUNT(team.game_id), AVG(team.ab), (SUM(team.h)*1.0)/SUM(team.ab), AVG(team.r),
                            AVG(team.hr), AVG(team.so), AVG(team.lob), AVG(team.ip), AVG(team.ra),
                            (SUM(team.er)*9.0)/SUM(team.ip), AVG(team.k), AVG(team.hra),
                            COUNT(opp.game_id), AVG(opp.ab), (SUM(opp.h)*1.0)/SUM(opp.ab), AVG(opp.r),
                            AVG(opp.hr), AVG(opp.so), AVG(opp.lob), AVG(opp.ip), AVG(opp.ra),
                            (SUM(opp.er)*9.0)/SUM(opp.ip), AVG(opp.k), AVG(opp.hra)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id
                        WHERE opp.team_id != ? AND team.team_id IN ( SELECT DISTINCT opp_id
                                                                        FROM team_stats AS ts
                                                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                                                            ON ts.game_id = gd.game_id
                                                                        WHERE team_id = ?)
                    """


nbaPlayerPosCmd = """
                    SELECT DISTINCT abrv
                        FROM lineups
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON lineups.game_id = gd.game_id
                        INNER JOIN player_positions AS pp
                            ON lineups.player_id = pp.player_id
                        INNER JOIN position_types AS pt
                            ON pp.pos_id = pt.pos_id
                        WHERE active = 1 AND pp.player_id = ?
                """


nbaPlayerStatsCmd = """
                        SELECT first_name, last_name, COUNT(ps.game_id), AVG(mins), AVG(pts), AVG(reb),
                                AVG(ast), AVG(stl), AVG(blk), AVG(trn), AVG(fls)
                            FROM player_stats AS ps
                            INNER JOIN ( {0[gdCmd]} ) AS gd
                                ON ps.game_id = gd.game_id {0[andGDCmd]}
                            LEFT JOIN players
                                ON players.player_id = ps.player_id
                            WHERE ps.player_id = ?
                    """


nbaTeamStatsCmd = """
                    SELECT COUNT(team.game_id), AVG(team.pts), AVG(team.fgm), AVG(team.ftm), AVG(team.tpm),
                            SUM(team.fgm)/(SUM(team.fga)*1.0), SUM(team.ftm)/(SUM(team.fta)*1.0),
                            SUM(team.tpm)/(SUM(team.tpa)*1.0), AVG(team.oreb), AVG(team.dreb), AVG(team.reb), AVG(team.ast), AVG(team.stl),
                            AVG(team.blk), AVG(team.trn), AVG(team.fls), AVG(team.pts_in_pt), AVG(team.fb_pts),
                            COUNT(opp.game_id), AVG(opp.pts), AVG(opp.fgm), AVG(opp.ftm), AVG(opp.tpm),
                            SUM(opp.fgm)/(SUM(opp.fga)*1.0), SUM(opp.ftm)/(SUM(opp.fta)*1.0),
                            SUM(opp.tpm)/(SUM(opp.tpa)*1.0), AVG(opp.oreb), AVG(opp.dreb), AVG(opp.reb), AVG(opp.ast), AVG(opp.stl),
                            AVG(opp.blk), AVG(opp.trn), AVG(opp.fls), AVG(opp.pts_in_pt), AVG(opp.fb_pts)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id {0[andGDCmd]}
                        WHERE team.team_id = ?
                    """

nbaOppStatsCmd = """
                    SELECT COUNT(team.game_id), AVG(team.pts), AVG(team.fgm), AVG(team.ftm), AVG(team.tpm),
                            SUM(team.fgm)/(SUM(team.fga)*1.0), SUM(team.ftm)/(SUM(team.fta)*1.0),
                            SUM(team.tpm)/(SUM(team.tpa)*1.0), AVG(team.oreb), AVG(team.dreb), AVG(team.reb), AVG(team.ast), AVG(team.stl),
                            AVG(team.blk), AVG(team.trn), AVG(team.fls), AVG(team.pts_in_pt), AVG(team.fb_pts),
                            COUNT(opp.game_id), AVG(opp.pts), AVG(opp.fgm), AVG(opp.ftm), AVG(opp.tpm),
                            SUM(opp.fgm)/(SUM(opp.fga)*1.0), SUM(opp.ftm)/(SUM(opp.fta)*1.0),
                            SUM(opp.tpm)/(SUM(opp.tpa)*1.0), AVG(opp.oreb), AVG(opp.dreb), Avg(opp.reb), AVG(opp.ast), AVG(opp.stl),
                            AVG(opp.blk), AVG(opp.trn), AVG(opp.fls), AVG(opp.pts_in_pt), AVG(opp.fb_pts)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id
                        WHERE opp.team_id != ? AND team.team_id IN ( SELECT DISTINCT opp_id
                                                                        FROM team_stats AS ts
                                                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                                                            ON ts.game_id = gd.game_id
                                                                        WHERE team_id = ?)
                    """



ncaabPlayerStatsCmd = """
                        SELECT first_name, last_name, abrv, COUNT(ps.game_id), AVG(mins), AVG(pts), AVG(reb),
                                AVG(ast), AVG(stl), AVG(blk), AVG(trn), AVG(fls)
                            FROM player_stats AS ps
                            INNER JOIN ( {0[gdCmd]} ) AS gd
                                ON ps.game_id = gd.game_id {0[andGDCmd]}
                            LEFT JOIN players
                                ON players.player_id = ps.player_id
                            LEFT JOIN position_types AS pt
                                ON players.pos_id = pt.pos_id
                            WHERE ps.player_id = ?
                    """

ncaabTeamStatsCmd = """
                    SELECT COUNT(team.game_id), AVG(team.pts), AVG(team.fgm), AVG(team.ftm), AVG(team.tpm),
                            SUM(team.fgm)/(SUM(team.fga)*1.0), SUM(team.ftm)/(SUM(team.fta)*1.0),
                            SUM(team.tpm)/(SUM(team.tpa)*1.0), AVG(team.oreb), AVG (team.dreb),
                            AVG(team.reb), AVG(team.ast), AVG(team.stl), AVG(team.blk), AVG(team.trn), AVG(team.fls),
                            COUNT(opp.game_id), AVG(opp.pts), AVG(opp.fgm), AVG(opp.ftm), AVG(opp.tpm),
                            SUM(opp.fgm)/(SUM(opp.fga)*1.0), SUM(opp.ftm)/(SUM(opp.fta)*1.0),
                            SUM(opp.tpm)/(SUM(opp.tpa)*1.0), AVG(opp.oreb), AVG (opp.dreb),
                            AVG(opp.reb), AVG(opp.ast), AVG(opp.stl), AVG(opp.blk), AVG(opp.trn), AVG(opp.fls)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id {0[andGDCmd]}
                        WHERE team.team_id = ?
                    """

ncaabOppStatsCmd = """
                    SELECT COUNT(team.game_id), AVG(team.pts), AVG(team.fgm), AVG(team.ftm), AVG(team.tpm),
                            SUM(team.fgm)/(SUM(team.fga)*1.0), SUM(team.ftm)/(SUM(team.fta)*1.0),
                            SUM(team.tpm)/(SUM(team.tpa)*1.0), AVG(team.oreb), AVG (team.dreb),
                            AVG(team.reb), AVG(team.ast), AVG(team.stl), AVG(team.blk), AVG(team.trn), AVG(team.fls),
                            COUNT(opp.game_id), AVG(opp.pts), AVG(opp.fgm), AVG(opp.ftm), AVG(opp.tpm),
                            SUM(opp.fgm)/(SUM(opp.fga)*1.0), SUM(opp.ftm)/(SUM(opp.fta)*1.0),
                            SUM(opp.tpm)/(SUM(opp.tpa)*1.0), AVG(opp.oreb), AVG (opp.dreb), AVG(opp.reb),
                            AVG(opp.ast), AVG(opp.stl), AVG(opp.blk), AVG(opp.trn), AVG(opp.fls)
                        FROM team_stats AS team
                        INNER JOIN team_stats AS opp
                            ON team.game_id = opp.game_id AND team.team_id = opp.opp_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON team.game_id = gd.game_id
                        WHERE opp.team_id != ? AND team.team_id IN ( SELECT DISTINCT opp_id
                                                                        FROM team_stats AS ts
                                                                        INNER JOIN ( {0[gdCmd]} ) AS gd
                                                                            ON ts.game_id = gd.game_id
                                                                        WHERE team_id = ?)
                    """


ouCmd = """
            SELECT IFNULL(overs.total,0), IFNULL(unders.total,0), IFNULL(push.total,0)
                FROM teams

                LEFT JOIN (
                            SELECT gl.team_id, COUNT(gl.game_id) AS total
                                FROM game_lines AS gl
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON gl.game_id = gd.game_id
                                INNER JOIN over_unders AS ov
                                    ON gl.game_id = ov.game_id
                                WHERE ov.outcome = 1
                                GROUP BY gl.team_id
                            ) AS overs
                    ON teams.team_id = overs.team_id

                LEFT JOIN (
                            SELECT gl.team_id, COUNT(gl.game_id) AS total
                                FROM game_lines AS gl
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON gl.game_id = gd.game_id
                                INNER JOIN over_unders AS ov
                                    ON gl.game_id = ov.game_id
                                WHERE ov.outcome = -1
                                GROUP BY gl.team_id
                            ) AS unders
                    ON teams.team_id = unders.team_id

                LEFT JOIN (
                            SELECT gl.team_id, COUNT(gl.game_id) AS total
                                FROM game_lines AS gl
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON gl.game_id = gd.game_id
                                INNER JOIN over_unders AS ov
                                    ON gl.game_id = ov.game_id
                                WHERE ov.outcome = 0
                                GROUP BY gl.team_id
                            ) AS push
                    ON teams.team_id = push.team_id

                WHERE teams.team_id = ?

        """


pitcherStats = """
                        SELECT SUM(w), SUM(l), SUM(IP), (SUM(er)*9.0)/SUM(ip), ((SUM(bba)+SUM(ha))*1.0)/SUM(ip), (SUM(k)*9.0)/SUM(ip), (SUM(hra)*9.0)/SUM(ip)
                            FROM pitcher_stats AS ps
                            INNER JOIN ( {0[gdCmd]} ) AS gd
                                ON ps.game_id = gd.game_id
                            WHERE player_id = ?
                    """

pitchResultCmd = """
                    SELECT COUNT({0[pType]}_id)
                        FROM ab_results AS ab
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON gd.game_id = ab.game_id
                        INNER JOIN players AS p
                            ON ab.{0[pType2]}_id = p.player_id
                        WHERE {0[pType]}_id = {0[playerId]} {0[andBT]} {0[andABType]}
                    """


# pitchResultCmd = """
#                     SELECT COUNT(ab_results.pitcher_id), (IFNULL(hits.total, 0)*1.0)/(COUNT(ab_results.pitcher_id)-bb.total), (IFNULL(k.total, 0)*100.0)/(COUNT(ab_results.pitcher_id)), (IFNULL(hrs.total,0)*100.0)/(COUNT(ab_results.pitcher_id)), (IFNULL(bb.total,0)*100.0)/COUNT(ab_results.pitcher_id)
#                         FROM ab_results
#                         INNER JOIN players
#                             ON ab_results.batter_id = players.player_id
#                         INNER JOIN pitches
#                             ON ab_results.pitch_id = pitches.pitch_id
#                         INNER JOIN ( {0[gdCmd]} ) AS gd
#                             ON ab_results.game_id = gd.game_id
#                         LEFT JOIN ( SELECT ab_results.pitcher_id, COUNT(ab_results.pitcher_id) AS total
#                                         FROM ab_results
#                                         INNER JOIN pitches
#                                             ON ab_results.pitch_id = pitches.pitch_id
#                                         INNER JOIN ( {0[gdCmd]} ) AS gd
#                                             ON ab_results.game_id = gd.game_id
#                                         INNER JOIN players
#                                             ON ab_results.batter_id = players.player_id
#                                         WHERE bats = '{0[bats]}' AND ab_type_id IN (2,6,8,15)
#                                         GROUP BY ab_results.pitcher_id
#                                     ) AS hits
#                             ON ab_results.pitcher_id = hits.pitcher_id
#
#                         LEFT JOIN ( SELECT ab_results.pitcher_id, COUNT(ab_results.pitcher_id) AS total
#                                         FROM ab_results
#                                         INNER JOIN pitches
#                                             ON ab_results.pitch_id = pitches.pitch_id
#                                         INNER JOIN ( {0[gdCmd]} ) AS gd
#                                             ON ab_results.game_id = gd.game_id
#                                         INNER JOIN players
#                                             ON ab_results.batter_id = players.player_id
#                                         WHERE bats = '{0[bats]}' AND ab_type_id = 8
#                                         GROUP BY ab_results.pitcher_id
#                                     ) AS hrs
#                             ON ab_results.pitcher_id = hrs.pitcher_id
#
#                         LEFT JOIN ( SELECT ab_results.pitcher_id, COUNT(ab_results.pitcher_id) AS total
#                                         FROM ab_results
#                                         INNER JOIN pitches
#                                             ON ab_results.pitch_id = pitches.pitch_id
#                                         INNER JOIN ( {0[gdCmd]} ) AS gd
#                                             ON ab_results.game_id = gd.game_id
#                                         INNER JOIN players
#                                             ON ab_results.batter_id = players.player_id
#                                         WHERE bats = '{0[bats]}' AND ab_type_id = 1
#                                         GROUP BY ab_results.pitcher_id
#                                     ) AS k
#                             ON ab_results.pitcher_id = k.pitcher_id
#
#                         LEFT JOIN ( SELECT ab_results.pitcher_id, COUNT(ab_results.pitcher_id) AS total
#                                         FROM ab_results
#                                         INNER JOIN pitches
#                                             ON ab_results.pitch_id = pitches.pitch_id
#                                         INNER JOIN ( {0[gdCmd]} ) AS gd
#                                             ON ab_results.game_id = gd.game_id
#                                         INNER JOIN players
#                                             ON ab_results.batter_id = players.player_id
#                                         WHERE bats = '{0[bats]}' AND ab_type_id = 4
#                                         GROUP BY ab_results.pitcher_id
#                                     ) AS bb
#                             ON ab_results.pitcher_id = bb.pitcher_id
#
#                         WHERE ab_results.pitcher_id = ? AND bats = '{0[bats]}'
#                 """


pitchTypeTotal = """
            		SELECT pitches.pitch_type_id, (COUNT(pitches.pitch_type_id)*100)/ ptotal.total, title, AVG(pitch_velocity)
            			FROM pitches
                        INNER JOIN ( SELECT pitcher_id, pitch_type_id, COUNT(pitcher_id) AS total
                                		FROM pitches
                                		INNER JOIN ( {0[gdCmd]} ) AS gd
                                            ON pitches.game_id = gd.game_id
                                		GROUP BY pitcher_id
                                    ) AS ptotal
                            ON pitches.pitcher_id = ptotal.pitcher_id
            			INNER JOIN pitch_types AS pt
            				ON pitches.pitch_type_id = pt.pitch_type_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON pitches.game_id = gd.game_id
            			WHERE pitches.pitcher_id = ?
                        GROUP BY pitches.pitch_type_id

            	"""


recordCmd = """
                SELECT IFNULL(wins.total,0), IFNULL(loses.total,0), IFNULL(draws.total, 0)

                    FROM teams

                    LEFT JOIN (
                                SELECT games.winner_id AS team_id, COUNT(games.game_id) AS total
                                    FROM games
                                    INNER JOIN ( {0[gdCmd]} ) AS gd
                                        ON games.game_id = gd.game_id
                                    GROUP BY games.winner_id
                                ) AS wins
                        ON teams.team_id = wins.team_id

                    LEFT JOIN (
                                SELECT games.loser_id AS team_id, COUNT(games.game_id) AS total
                                    FROM games
                                    INNER JOIN ( {0[gdCmd]} ) AS gd
                                        ON games.game_id = gd.game_id
                                    GROUP BY games.loser_id
                                ) AS loses
                        ON teams.team_id = loses.team_id

                    LEFT JOIN (
                                SELECT teams.team_id, COUNT(games.game_id) AS total
                                    FROM games
                                    INNER JOIN ( {0[gdCmd]} ) AS gd
                                        ON games.game_id = gd.game_id
                                    INNER JOIN teams
                                        ON games.home_id = teams.team_id OR games.away_id = teams.team_id
                                    WHERE outcome = 'tied'
                                    GROUP BY teams.team_id
                                ) AS draws
                        ON teams.team_id = draws.team_id

                    WHERE teams.team_id = ?

        """


teamInfoCmd = """
                SELECT team_id, abrv, first_name, last_name, primary_color, secondary_color
                    FROM teams
                    WHERE team_id = ?
                """
