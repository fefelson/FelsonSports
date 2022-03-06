from copy import deepcopy
from datetime import datetime, date, timedelta

from .. import Environ as ENV
from ..Interfaces import Fileable
from ..Models import yId
from ..Utils.SQL import formGDCmd, getGDCmds

from pprint import pprint

################################################################################
################################################################################


passingCmd = """
                SELECT att.value, comp.value/att.value,
                        yds.value, yds.value/comp.value, tds.value, ints.value, rating.value
                    FROM lineups

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 102
                                    GROUP BY player_id
                                ) AS comp
                        ON lineups.team_id = comp.team_id AND lineups.player_id = comp.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 103
                                    GROUP BY player_id
                                ) AS att
                        ON lineups.team_id = att.team_id AND lineups.player_id = att.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 105
                                    GROUP BY player_id
                                ) AS yds
                        ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 108
                                    GROUP BY player_id
                                ) AS tds
                        ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id


                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 109
                                    GROUP BY player_id
                                ) AS ints
                        ON lineups.team_id = ints.team_id AND lineups.player_id = ints.player_id


                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 113
                                    GROUP BY player_id
                                ) AS rating
                        ON lineups.team_id = rating.team_id AND lineups.player_id = rating.player_id

                    GROUP BY lineups.player_id
    """

ncaafRushingCmd = """
                SELECT att.value, yds.value,
                        yds.value/att.value, tds.value
                    FROM lineups
                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 202
                                    GROUP BY player_id
                                ) AS att
                        ON lineups.team_id = att.team_id AND lineups.player_id = att.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 203
                                    GROUP BY player_id
                                ) AS yds
                        ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 207
                                    GROUP BY player_id
                                ) AS tds
                        ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id

                    GROUP BY lineups.player_id

    """


nflRushingCmd = """
                SELECT att.value, yds.value,
                        yds.value/att.value, tds.value, fum.value
                    FROM lineups
                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 202
                                    GROUP BY player_id
                                ) AS att
                        ON lineups.team_id = att.team_id AND lineups.player_id = att.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 203
                                    GROUP BY player_id
                                ) AS yds
                        ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 207
                                    GROUP BY player_id
                                ) AS tds
                        ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 3
                                    GROUP BY player_id
                                ) AS fum
                        ON lineups.team_id = fum.team_id AND lineups.player_id = fum.player_id

                    GROUP BY lineups.player_id

    """



ncaafReceivingCmd = """
                SELECT rec.value, yds.value,
                        yds.value/rec.value, tds.value
                    FROM lineups

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 302
                                    GROUP BY player_id
                                ) AS rec
                        ON lineups.team_id = rec.team_id AND lineups.player_id = rec.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 303
                                    GROUP BY player_id
                                ) AS yds
                        ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 309
                                    GROUP BY player_id
                                ) AS tds
                        ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id

                    GROUP BY lineups.player_id
    """


nflReceivingCmd = """
                SELECT tgt.value, rec.value, yds.value,
                        yds.value/rec.value, tds.value, fum.value
                    FROM lineups

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 310
                                    GROUP BY player_id
                                ) AS tgt
                        ON lineups.team_id = tgt.team_id AND lineups.player_id = tgt.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 302
                                    GROUP BY player_id
                                ) AS rec
                        ON lineups.team_id = rec.team_id AND lineups.player_id = rec.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 303
                                    GROUP BY player_id
                                ) AS yds
                        ON lineups.team_id = yds.team_id AND lineups.player_id = yds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 309
                                    GROUP BY player_id
                                ) AS tds
                        ON lineups.team_id = tds.team_id AND lineups.player_id = tds.player_id

                    INNER JOIN (
                                SELECT team_id, player_id, AVG(value) AS value
                                    FROM ( {0[gdCmd]} ) AS gd
                                    INNER JOIN player_stats AS ts
                                        ON gd.game_id = ts.game_id {0[andTS]}
                                    WHERE stat_id = 3
                                    GROUP BY player_id
                                ) AS fum
                        ON lineups.team_id = fum.team_id AND lineups.player_id = fum.player_id

                    GROUP BY lineups.player_id
    """




ncaaBBallTeamStatCmd = """
                        SELECT AVG(fga), SUM(fgm)/(SUM(fga)*1.0), AVG(fta),
                                SUM(ftm)/(SUM(fta)*1.0), AVG(tpa), SUM(tpm)/(SUM(tpa)*1.0), AVG(pts),
                                AVG(oreb), AVG(dreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn),
                                AVG(fls)
                            FROM ( {0[gdCmd]} ) AS gd
                            INNER JOIN team_stats AS ts
                                ON gd.game_id = ts.game_id {0[andTS]}
                            GROUP BY ts.team_id
                        """


bballPlayerStatCmd = """
                        SELECT AVG(starter), AVG(fga), SUM(fgm)/(SUM(fga)*1.0), AVG(fta),
                                SUM(ftm)/(SUM(fta)*1.0), AVG(tpa), SUM(tpm)/(SUM(tpa)*1.0), AVG(pts),
                                AVG(oreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn),
                                AVG(fls), AVG(mins), AVG(plmn)
                            FROM ( {0[gdCmd]} ) AS gd
                            INNER JOIN player_stats AS ts
                                ON gd.game_id = ts.game_id {0[andTS]}
                            INNER JOIN lineups
                                ON ts.game_id = lineups.game_id AND ts.player_id = lineups.player_id
                            GROUP BY ts.player_id
            """


ncaabPlayerStatCmd = """
                        SELECT AVG(starter), AVG(fga), SUM(fgm)/(SUM(fga)*1.0), AVG(fta),
                                SUM(ftm)/(SUM(fta)*1.0), AVG(tpa), SUM(tpm)/(SUM(tpa)*1.0), AVG(pts),
                                AVG(oreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn),
                                AVG(fls), AVG(mins)
                            FROM ( {0[gdCmd]} ) AS gd
                            INNER JOIN player_stats AS ts
                                ON gd.game_id = ts.game_id {0[andTS]}
                            INNER JOIN lineups
                                ON ts.game_id = lineups.game_id AND ts.player_id = lineups.player_id
                            GROUP BY ts.player_id
            """

bballTeamStatCmd = """
                        SELECT AVG(fga), SUM(fgm)/(SUM(fga)*1.0), AVG(fta),
                                SUM(ftm)/(SUM(fta)*1.0), AVG(tpa), SUM(tpm)/(SUM(tpa)*1.0), AVG(pts),
                                AVG(oreb), AVG(dreb), AVG(reb), AVG(ast), AVG(stl), AVG(blk), AVG(trn),
                                AVG(fls), AVG(pts_in_pt), AVG(fb_pts)
                            FROM ( {0[gdCmd]} ) AS gd
                            INNER JOIN team_stats AS ts
                                ON gd.game_id = ts.game_id {0[andTS]}
                            GROUP BY ts.team_id
                    """


batPlayerCmd = """
                SELECT SUM(ab), SUM(r), SUM(bb), SUM(h), SUM(hr), SUM(rbi), SUM(sb),
                        SUM(tb), SUM(so), (SUM(h)*1.0)/SUM(ab) AS ba,
                        ((SUM(hbp)+SUM(bb)+SUM(h)*1.0)/SUM(pa)) AS obp,
                        ((SUM(tb)*1.0)/SUM(ab)) AS slg,
                        ((SUM(hbp)+SUM(bb)+SUM(h)*1.0)/SUM(pa))+((SUM(tb)*1.0)/SUM(ab)) AS ops
                FROM ( {0[gdCmd]} ) AS gd
                INNER JOIN batter_stats AS bs
                    ON gd.game_id = bs.game_id {0[andBS]}
                GROUP BY bs.player_id
                HAVING SUM(ab) > ?
            """


mlbTeamCmd = """
            SELECT SUM((CASE WHEN ts.team_id = winner_id THEN 1 ELSE 0 END)) AS wins,
                    SUM((CASE WHEN ts.team_id = loser_id THEN 1 ELSE 0 END)) AS loses,
                    SUM(ab), SUM(r), SUM(bb), SUM(h), SUM(hr), SUM(rbi), SUM(sb), SUM(so),
                    SUM(lob), (SUM(h)*1.0)/SUM(ab) AS ba, ((SUM(bb)+SUM(h)*1.0)/SUM(ab)+SUM(bb)) AS obp,
                    SUM(ip), SUM(ra), (SUM(er)*9.0)/SUM(ip), (SUM(bba)+SUM(ha))/SUM(ip),
                    (SUM(k)*9.0)/SUM(ip), SUM(hra)
                FROM ( {0[gdCmd]} ) AS gd
                INNER JOIN team_stats AS ts
                    ON gd.game_id = ts.game_id {0[andTS]}
                GROUP BY ts.team_id
            """



mlbTeamGameCmd = """
                SELECT SUM((CASE spread_outcome WHEN 1 THEN 1 ELSE 0 END)) ats_wins,
                        SUM((CASE spread_outcome WHEN -1 THEN 1 ELSE 0 END)) AS ats_loses,
                        AVG(spread), AVG(result), AVG(line), AVG(money),
                        SUM((CASE WHEN spread_outcome == 1 AND line > 0 THEN 100+line
                                WHEN spread_outcome == 1 AND line < 0 THEN (10000/(line*-1.0))+100
                                ELSE 0 END)),
                        SUM((CASE WHEN money_outcome == 1 AND money > 0 THEN 100+money
                                WHEN money_outcome == 1 AND money < 0 THEN (10000/(money*-1.0))+100
                                ELSE 0 END))
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN game_lines AS gl
                        ON gd.game_id = gl.game_id {0[andGL]}
                    GROUP BY gl.team_id
                """


ncaafTeamGameCmd = """
                SELECT SUM((CASE spread_outcome WHEN 1 THEN 1 ELSE 0 END)) ats_wins,
                        SUM((CASE spread_outcome WHEN -1 THEN 1 ELSE 0 END)) AS ats_loses,
                        SUM((CASE spread_outcome WHEN 0 THEN 1 ELSE 0 END)) AS ats_push,
                        AVG(spread), AVG(result), AVG(line), AVG(money),
                        SUM((CASE WHEN spread_outcome == 1 AND line > 0 THEN 100+line
                                WHEN spread_outcome == 1 AND line < 0 THEN (10000/(line*-1.0))+100
                                WHEN spread_outcome == 0 THEN 100
                                ELSE 0 END)),
                        SUM((CASE WHEN money_outcome == 1 AND money > 0 THEN 100+money
                                WHEN money_outcome == 1 AND money < 0 THEN (10000/(money*-1.0))+100
                                ELSE 0 END)),
                        AVG(ou), AVG(over_line), AVG(under_line), AVG(ov.total),
                        SUM((CASE WHEN outcome == 1 AND line > 0 THEN 100+over_line
                                WHEN outcome == 1 AND line < 0 THEN (10000/(over_line*-1.0))+100
                                WHEN outcome == 0 THEN 100
                                ELSE 0 END)),
                        SUM((CASE WHEN outcome == -1 AND line > 0 THEN 100+under_line
                                WHEN outcome == -1 AND line < 0 THEN (10000/(under_line*-1.0))+100
                                WHEN outcome == 0 THEN 100
                                ELSE 0 END))
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN game_lines AS gl
                        ON gd.game_id = gl.game_id {0[andGL]}
                    INNER JOIN over_unders AS ov
                        ON gl.game_id = ov.game_id
                    GROUP BY gl.team_id
                """


ncaafTeamStatCmd = """
                SELECT AVG(value)
                    FROM team_stats AS ts
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON ts.game_id = gd.game_id {0[andTS]}
                    INNER JOIN stat_types AS st
                        ON ts.stat_id = st.stat_id
                    WHERE st.abrv = ?
                    GROUP BY team_id
                """

ncaafTeamPlayerStatCmd = """
                SELECT AVG(value)
                    FROM (SELECT SUM(value) AS value, team_id
                                FROM player_stats AS ts
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ts.game_id = gd.game_id {0[andTS]}
                                INNER JOIN stat_types AS st
                                    ON ts.stat_id = st.stat_id
                                WHERE st.abrv = ?
                                GROUP BY ts.game_id, team_id)
                    GROUP by team_id
                """



pitchPlayerCmd = """
                SELECT SUM(w), SUM(l), SUM(sv), SUM(ip), SUM(bba), SUM(ha), SUM(k), SUM(hra),
                        (SUM(er)*9.0)/SUM(ip), (SUM(bba)+SUM(ha))/SUM(ip), (SUM(k)*9)/SUM(ip)
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN pitcher_stats AS ps
                        ON gd.game_id = ps.game_id {0[andPS]}
                    INNER JOIN bullpens AS bp
                        ON gd.game_id = bp.game_id AND ps.player_id = bp.player_id
                    WHERE pitch_order > 1
                    GROUP BY ps.player_id
                    HAVING SUM(ip) > ?
                """


startPlayerCmd = """
                SELECT SUM(w), SUM(l), SUM(sv), SUM(ip), SUM(bba), SUM(ha), SUM(k), SUM(hra),
                        (SUM(er)*9.0)/SUM(ip), (SUM(bba)+SUM(ha))/SUM(ip), (SUM(k)*9)/SUM(ip)
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN pitcher_stats AS ps
                        ON gd.game_id = ps.game_id {0[andPS]}
                    INNER JOIN bullpens AS bp
                        ON gd.game_id = bp.game_id AND ps.player_id = bp.player_id
                    WHERE pitch_order = 1
                    GROUP BY ps.player_id
                    HAVING SUM(ip) > ?
                """


startGameCmd = """
                SELECT SUM((CASE spread_outcome WHEN 1 THEN 1 ELSE 0 END)) ats_wins,
                        SUM((CASE spread_outcome WHEN -1 THEN 1 ELSE 0 END)) AS ats_loses,
                        AVG(spread), AVG(result), AVG(line), AVG(money),
                        SUM((CASE WHEN spread_outcome == 1 AND line > 0 THEN 100+line
                                WHEN spread_outcome == 1 AND line < 0 THEN 100+(10000/(line*-1.0))
                                ELSE 0 END)),
                        SUM((CASE WHEN money_outcome == 1 AND money > 0 THEN 100+money
                                WHEN money_outcome == 1 AND money < 0 THEN 100+(10000/(money*-1.0))
                                    ELSE 0 END))
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN game_lines AS gl
                        ON gd.game_id = gl.game_id {0[andGL]}
                    INNER JOIN bullpens AS bp
                        ON gd.game_id = bp.game_id
                    WHERE pitch_order = 1
                    GROUP BY player_id
                """



timeFrame = ("Season", "2Months", "1Month", "2Weeks")


today = date.today()
twoWeeks = today - timedelta(14)
oneMonth = today - timedelta(30)
twoMonths = today - timedelta(60)





################################################################################
################################################################################

_awayHomeDict = dict([(label, {}) for label in ("all", "away", "home")])
_winLossDict = dict([(label, {}) for label in ("all", "winner", "loser")])
_awayWinDict =  dict([(label, deepcopy(_winLossDict)) for label in ("all", "away", "home")])


class Report(Fileable):


    _info =  {"playerStats": {},
                "bullpenStats":{},
                "starterStats":{},
                "teamStats": {},
                "teamGaming":{},
                "startGaming":{},
                "batterStats":{},
                "leagueId": None,
                "lastUpdate": str(datetime.today()),
                }

    _reportFilePath = None


    def __init__(self, league, *args, **kwargs):
        Fileable.__init__(self, self._info, *args, **kwargs)

        self.league = league



    def create(self):
        self.setFilePath()
        print("new Report", self.filePath)
        self.info = deepcopy(self._info)
        self.reportData()
        self.write()


    def score(self, stat, data):
        values = sorted([x[stat] for x in data if x[stat]])
        sDict = {}


        sDict[1] = values[int(.9*len(values))]
        sDict[2] = values[int(.8*len(values))]
        sDict[3] = values[int(.6*len(values))]
        sDict[4] = values[int(.4*len(values))]
        sDict[5] = values[int(.2*len(values))]

        return sDict.copy()


    def playerScore(self, stat, data):
        values = sorted([x[stat] for x in data if x[stat]])
        sDict = {}


        sDict[1] = values[int(.95*len(values))]
        sDict[2] = values[int(.9*len(values))]
        sDict[3] = values[int(.8*len(values))]
        sDict[4] = values[int(.7*len(values))]
        sDict[5] = values[int(.6*len(values))]

        return sDict.copy()


    def teamScore(self, stat, data):
        values = sorted([x[stat] for x in data if x[stat]])
        sDict = {}


        sDict[1] = values[int(.9*len(values))]
        sDict[2] = values[int(.8*len(values))]
        sDict[3] = values[int(.6*len(values))]
        sDict[4] = values[int(.4*len(values))]
        sDict[5] = values[int(.2*len(values))]

        return sDict.copy()


    def score1(self, data):
        values = sorted(data)
        sDict = {}

        try:
            sDict[1] = values[int(.95*len(values))]
            sDict[2] = values[int(.9*len(values))]
            sDict[3] = values[int(.8*len(values))]
            sDict[4] = values[int(.6*len(values))]
            sDict[5] = values[int(.5*len(values))]
        except IndexError:
            pass

        return sDict.copy()


    def setFilePath(self):
        self.filePath = ENV.reportFilePath.format(self._info)


    def reportData(self):
        pass





################################################################################
################################################################################




class MLBReport(Report):


    _batStats = ("ab", "r", "bb", "h", "hr", "rbi", "sb", "tb", "so", "avg", "obp", "slg", "ops")
    _pitchStats = ("w","l", "sv", "ip", "bba", "ha", "k", "hra", "era", "whip", "k9")
    _startGaming = ("atsW", "atsL", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$")
    _teamStats = ("w", "l", "ab","r","bb", "h", "hr","rbi","sb","so","lob","avg", "obp", "ip","ra","era","whip","k9","hra")
    _teamGaming = ("atsW", "atsL", "atsP", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$", "ou", "overLine", "underLine", "total", "over$", "under$")


    _info =  {"batterStats": dict(zip(timeFrame, [deepcopy(_awayHomeDict) for _ in timeFrame])),
                "teamStats": dict(zip(timeFrame, [deepcopy(_awayHomeDict) for _ in timeFrame])),
                "teamGaming": dict(zip(timeFrame, [deepcopy(_awayHomeDict) for _ in timeFrame])),
                "bullpenStats": dict(zip(timeFrame, [deepcopy(_awayHomeDict) for _ in timeFrame])),
                "starterStats": dict(zip(timeFrame, [deepcopy(_awayHomeDict) for _ in timeFrame])),
                "startGaming": dict(zip(timeFrame, [deepcopy(_awayHomeDict) for _ in timeFrame])),
                "leagueId": "mlb",
                "lastUpdate": str(datetime.today()),
                }



    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)




    def reportData(self):
        abLimits = dict(zip(timeFrame, (150,80,40,20)))
        bullLimits = dict(zip(timeFrame, (52,24,14,6)))
        startLimits = dict(zip(timeFrame, (120,30,15,10)))
        currentSeason = self.league.fileManager.info["currentSeason"]
        gdCmds = {"Season": formGDCmd(currentSeason),
                    "2Weeks": formGDCmd(currentSeason, twoWeeks),
                    "1Month": formGDCmd(currentSeason, oneMonth),
                    "2Months": formGDCmd(currentSeason, twoMonths)
                }
        for tF in timeFrame:
            for hA in ("all", "away", "home"):
                div = 1 if hA == "all" else 2
                gdCmd = gdCmds[tF]
                andBS = "" if hA == "all" else "AND gd.{}_id = bs.team_id".format(hA)
                andTS = "" if hA == "all" else "AND gd.{}_id = ts.team_id".format(hA)
                andPS = "" if hA == "all" else "AND gd.{}_id = ps.team_id".format(hA)
                andGL = "" if hA == "all" else "AND gd.{}_id = gl.team_id".format(hA)


                batData = [dict(zip(self._batStats, player)) for player in self.league.dbManager.fetchAll(batPlayerCmd.format({"gdCmd":gdCmd, "andBS":andBS}), (abLimits[tF]/div,))]
                teamData = [dict(zip(self._teamStats, player)) for player in self.league.dbManager.fetchAll(mlbTeamCmd.format({"gdCmd":gdCmd, "andTS":andTS}))]
                startData = [dict(zip(self._pitchStats, player)) for player in self.league.dbManager.fetchAll(startPlayerCmd.format({"gdCmd":gdCmd, "andPS":andPS}), (startLimits[tF]/div,))]
                bullData = [dict(zip(self._pitchStats, player)) for player in self.league.dbManager.fetchAll(pitchPlayerCmd.format({"gdCmd":gdCmd, "andPS":andPS}), (bullLimits[tF]/div,))]
                gameData = [dict(zip(self._teamGaming, player)) for player in self.league.dbManager.fetchAll(mlbTeamGameCmd.format({"gdCmd":gdCmd, "andGL":andGL}))]
                startGameData = [dict(zip(self._startGaming, player)) for player in self.league.dbManager.fetchAll(startGameCmd.format({"gdCmd":gdCmd, "andGL":andGL}))]

                for stat in self._batStats:
                    self.info["batterStats"][tF][hA][stat] = self.score(stat, batData, True)

                for stat in self._pitchStats:
                    if stat in ("bba", "ha", "hra", "era","whip", "l"):
                        reverse = False
                    else:
                        reverse = True

                    self.info["starterStats"][tF][hA][stat] = self.score(stat, startData)
                    self.info["bullpenStats"][tF][hA][stat] = self.score(stat, bullData)

                for stat in self._teamStats:
                    if stat in ("lob","so","era","whip","ra","hra"):
                        reverse = False
                    else:
                        reverse = True
                    self.info["teamStats"][tF][hA][stat] = self.score(stat, teamData)

                for stat in self._startGaming:

                    if stat in ("ats$", "money$"):
                        data = []
                        for x in startGameData:
                            total = (x["atsW"]+x["atsL"])*100
                            result = x[stat]
                            data.append({stat:((result-total)/total)*100})
                        self.info["startGaming"][tF][hA][stat] = self.score(stat, data)
                    else:
                        self.info["startGaming"][tF][hA][stat] = self.score(stat, startGameData)


                for stat in self._teamGaming:

                    if stat in ("ats$", "money$"):
                        data = []
                        for x in gameData:
                            total = (x["atsW"]+x["atsL"])*100
                            result = x[stat]
                            data.append({stat:((result-total)/total)*100})
                        self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                    else:
                        self.info["teamGaming"][tF][hA][stat] = self.score(stat, gameData)


################################################################################
################################################################################


class NCAAFReport(Report):


    _teamGaming = ("atsW", "atsL", "atsP", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$", "ou", "overLine", "underLine", "total", "over$", "under$")
    _passList = ("att", "comp%", "yds", "avg", "td", "int", "rating")
    _rushList = ("car", "yds", "avg", "td")
    _recList = ("rec", "yds", "avg", "td")


    _info =  {
                "teamGaming": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                "teamStats": {"regular": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                                "reverse": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices]))
                            },
                "playerStats": {"passing": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                                "rushing": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                                "receiving": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices]))
                            },
                "leagueId": "ncaaf",
                "lastUpdate": str(datetime.today()),
                }


    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def reportData(self):
        currentSeason = self.league.fileManager.info["currentSeason"]
        gdCmds = getGDCmds(int(currentSeason))
        timeFrame = ENV.tFFootballChoices
        currentSeason = self.league.fileManager.info["currentSeason"]

        teamStatList = [x[0] for x in self.league.dbManager.fetchAll("SELECT abrv FROM stat_types WHERE stat_id > 900")]



        for tF in timeFrame:
            for hA in ("all", "away", "home"):
                teamStats = {}
                gdCmd = gdCmds[tF]

                andTS = "" if hA == "all" else "AND gd.{}_id = ts.team_id".format(hA)
                andGL = "" if hA == "all" else "AND gd.{}_id = gl.team_id".format(hA)

                gameData = [dict(zip(self._teamGaming, player)) for player in self.league.dbManager.fetchAll(ncaafTeamGameCmd.format({"gdCmd":gdCmd, "andGL":andGL}))]


                for stat in self._teamGaming:
                    try:

                        if stat in ("ats$", "money$"):
                            data = []
                            for x in gameData:
                                total = (x["atsW"]+x["atsL"]+x["atsP"])*100
                                result = x[stat]
                                data.append({stat:((result-total)/total)*100})
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                        else:
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, gameData)
                    except IndexError:
                        pass


                for label in teamStatList:
                    teamData = [x[0] for x in self.league.dbManager.fetchAll(ncaafTeamStatCmd.format({"gdCmd": gdCmd, "andTS": andTS}), (label,))]
                    if label in ("TmPaSACKS", "TO", "PEN", "PENYds", "PaTDs", "RuTDs", "TmFum", "TmINTS"):
                        self.info["teamStats"]["regular"][tF][hA][label] = self.score1(teamData)
                        self.info["teamStats"]["reverse"][tF][hA][label] = self.score1(teamData)
                    else:
                        self.info["teamStats"]["regular"][tF][hA][label] = self.score1(teamData)
                        self.info["teamStats"]["reverse"][tF][hA][label] = self.score1(teamData)

                for label in ("PaTDs", "RuTDs"):
                    teamData = [x[0] for x in self.league.dbManager.fetchAll(ncaafTeamPlayerStatCmd.format({"gdCmd": gdCmd, "andTS": andTS}), (label, ))]
                    self.info["teamStats"]["regular"][tF][hA][label] = self.score1(teamData)
                    self.info["teamStats"]["reverse"][tF][hA][label] = self.score1(teamData)


                for label in ("passing", "rushing", "receiving"):
                    statCmd, statList = {"passing": (passingCmd, self._passList), "rushing": (ncaafRushingCmd, self._rushList), "receiving": (ncaafReceivingCmd, self._recList)}[label]

                    playerData = [dict(zip(statList, player)) for player in self.league.dbManager.fetchAll(statCmd.format({"gdCmd": gdCmd, "andTS": andTS}))]
                    pprint(playerData)
                    for stat in statList:
                        if stat in ("ints", "fum",):
                            self.info["playerStats"][label][tF][hA][stat] = self.score(stat, playerData)
                        else:
                            self.info["playerStats"][label][tF][hA][stat] = self.score(stat, playerData)


################################################################################
################################################################################


class NFLReport(Report):


    _teamGaming = ("atsW", "atsL", "atsP", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$", "ou", "overLine", "underLine", "total", "over$", "under$")
    _passList = ("att", "comp%", "yds", "avg", "td", "int", "rating")
    _rushList = ("car", "yds", "avg", "td", "fum")
    _recList = ("tgt", "rec", "yds", "avg", "td", "fum")

    _info =  {
                "teamGaming": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                "teamStats": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                "playerStats": {"passing": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                                "rushing": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices])),
                                "receiving": dict(zip(ENV.tFFootballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFFootballChoices]))
                            },
                "leagueId": "nfl",
                "lastUpdate": str(datetime.today()),
                }


    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def reportData(self):
        currentSeason = self.league.fileManager.info["currentSeason"]
        gdCmds = getGDCmds(int(currentSeason))
        timeFrame = ENV.tFFootballChoices
        currentSeason = self.league.fileManager.info["currentSeason"]

        teamStatList = [x[0] for x in self.league.dbManager.fetchAll("SELECT abrv FROM stat_types WHERE stat_id > 900")]

        for tF in timeFrame:
            for hA in ("all", "away", "home"):
                teamStats = {}
                gdCmd = gdCmds[tF]

                andTS = "" if hA == "all" else "AND gd.{}_id = ts.team_id".format(hA)
                andGL = "" if hA == "all" else "AND gd.{}_id = gl.team_id".format(hA)

                gameData = [dict(zip(self._teamGaming, player)) for player in self.league.dbManager.fetchAll(ncaafTeamGameCmd.format({"gdCmd":gdCmd, "andGL":andGL}))]

                for stat in self._teamGaming:
                    try:

                        if stat in ("ats$", "money$", "over$", "under$"):
                            data = []
                            for x in gameData:
                                total = (x["atsW"]+x["atsL"]+x["atsP"])*100
                                result = x[stat]
                                data.append({stat:((result-total)/total)*100})
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                        else:
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, gameData)
                    except IndexError:
                        pass

                for label in teamStatList:
                    teamData = [x[0] for x in self.league.dbManager.fetchAll(ncaafTeamStatCmd.format({"gdCmd": gdCmd, "andTS": andTS}), (label,))]
                    self.info["teamStats"][tF][hA][label] = self.score1(teamData)

                for label in ("PaTDs", "RuTDs"):
                    teamData = [x[0] for x in self.league.dbManager.fetchAll(ncaafTeamPlayerStatCmd.format({"gdCmd": gdCmd, "andTS": andTS}), (label, ))]
                    self.info["teamStats"][tF][hA][label] = self.score1(teamData)

                for label in ("passing", "rushing", "receiving"):
                    print(label, tF, hA)
                    statCmd, statList = {"passing": (passingCmd, self._passList), "rushing": (nflRushingCmd, self._rushList), "receiving": (nflReceivingCmd, self._recList)}[label]

                    playerData = [dict(zip(statList, player)) for player in self.league.dbManager.fetchAll(statCmd.format({"gdCmd": gdCmd, "andTS": andTS}))]
                    for stat in statList:
                        self.info["playerStats"][label][tF][hA][stat] = self.score(stat, playerData)


################################################################################
################################################################################


class NBAReport(Report):


    _teamGaming = ("atsW", "atsL", "atsP", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$", "ou", "overLine", "underLine", "total", "over$", "under$")

    _info =  {
                "teamGaming": dict(zip(ENV.tFBasketballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFBasketballChoices])),
                "teamStats": dict(zip(ENV.tFBasketballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFBasketballChoices])),
                "playerStats": dict(zip(ENV.tFBasketballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFBasketballChoices])),
                "leagueId": "nba",
                "lastUpdate": str(datetime.today()),
                }



    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def reportData(self):
        currentSeason = self.league.fileManager.info["currentSeason"]
        gdCmds = getGDCmds(int(currentSeason))
        timeFrame = ENV.tFBasketballChoices

        teamStatList = ("fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts", "oreb", "dreb", "reb",
                            "ast", "stl", "blk", "trn", "fls", "pts_in_pt", "fb_pts")

        playerStatList = ("start%","fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts", "oreb",  "reb",
                    "ast", "stl", "blk", "trn", "fls", "mins", "plmn")

        for tF in timeFrame:

            gdCmd = gdCmds[tF]

            for hA in ("all", "away", "home"):


                andTS = "" if hA == "all" else "AND gd.{}_id = ts.team_id".format(hA)
                andGL = "" if hA == "all" else "AND gd.{}_id = gl.team_id".format(hA)

                gameData = [dict(zip(self._teamGaming, player)) for player in self.league.dbManager.fetchAll(ncaafTeamGameCmd.format({"gdCmd":gdCmd, "andGL":andGL}))]

                for stat in self._teamGaming:
                    try:
                        if stat in ("ats$", "money$"):
                            data = []
                            for x in gameData:
                                total = (x["atsW"]+x["atsL"]+x["atsP"])*100
                                result = x[stat]
                                data.append({stat:((result-total)/total)*100})
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                        elif stat in ("over$", "under$"):
                            data = []
                            for x in gameData:
                                total = (x["atsW"]+x["atsL"]+x["atsP"])*100
                                result = x[stat]
                                data.append({stat:((result-total)/total)*100})
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                        else:
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, gameData)
                    except IndexError:
                        pass


                teamData = [dict(zip(teamStatList, player)) for player in self.league.dbManager.fetchAll(bballTeamStatCmd.format({"gdCmd":gdCmd, "andTS":andTS}))]
                playerData = [dict(zip(playerStatList, player)) for player in self.league.dbManager.fetchAll(bballPlayerStatCmd.format({"gdCmd":gdCmd, "andTS":andTS}))]

                for label in teamStatList:
                    self.info["teamStats"][tF][hA][label] = self.teamScore(label, teamData)

                for label in playerStatList:
                    self.info["playerStats"][tF][hA][label] = self.playerScore(label, playerData)


################################################################################
################################################################################


class NCAABReport(Report):


    _teamGaming = ("atsW", "atsL", "atsP", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$", "ou", "overLine", "underLine", "total", "over$", "under$")

    _info =  {
                "teamGaming": dict(zip(ENV.tFBasketballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFBasketballChoices])),
                "teamStats": dict(zip(ENV.tFBasketballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFBasketballChoices])),
                "playerStats": dict(zip(ENV.tFBasketballChoices, [deepcopy(_awayHomeDict) for _ in ENV.tFBasketballChoices])),
                "leagueId": "ncaab",
                "lastUpdate": str(datetime.today()),
                }


    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def reportData(self):
        currentSeason = self.league.fileManager.info["currentSeason"]
        gdCmds = getGDCmds(int(currentSeason))
        timeFrame = ENV.tFBasketballChoices

        teamStatList = ("fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts", "oreb", "dreb", "reb",
                            "ast", "stl", "blk", "trn", "fls")

        playerStatList = ("start%","fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts", "oreb",  "reb",
                    "ast", "stl", "blk", "trn", "fls", "mins")

        for tF in timeFrame:

            gdCmd = gdCmds[tF]

            for hA in ("all", "away", "home"):

                andTS = "" if hA == "all" else "AND gd.{}_id = ts.team_id".format(hA)
                andGL = "" if hA == "all" else "AND gd.{}_id = gl.team_id".format(hA)

                gameData = [dict(zip(self._teamGaming, player)) for player in self.league.dbManager.fetchAll(ncaafTeamGameCmd.format({"gdCmd":gdCmd, "andGL":andGL}))]

                for stat in self._teamGaming:
                    try:
                        if stat in ("ats$", "money$"):
                            data = []
                            for x in gameData:
                                total = (x["atsW"]+x["atsL"]+x["atsP"])*100
                                result = x[stat]
                                data.append({stat:((result-total)/total)*100})
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                        elif stat in ("over$", "under$"):
                            data = []
                            for x in gameData:
                                total = (x["atsW"]+x["atsL"]+x["atsP"])*100
                                result = x[stat]
                                data.append({stat:((result-total)/total)*100})
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, data)
                        else:
                            self.info["teamGaming"][tF][hA][stat] = self.score(stat, gameData)
                    except IndexError:
                        pass


                teamData = [dict(zip(teamStatList, player)) for player in self.league.dbManager.fetchAll(ncaaBBallTeamStatCmd.format({"gdCmd":gdCmd, "andTS":andTS}))]
                playerData = [dict(zip(playerStatList, player)) for player in self.league.dbManager.fetchAll(ncaabPlayerStatCmd.format({"gdCmd":gdCmd, "andTS":andTS}))]

                for label in teamStatList:
                    # print(label)
                    self.info["teamStats"][tF][hA][label] = self.teamScore(label, teamData)


                for label in playerStatList:
                    self.info["playerStats"][tF][hA][label] = self.playerScore(label, playerData)


    def playerScore(self, stat, data):
        values = sorted([x[stat] for x in data if x[stat]])
        sDict = {}


        sDict[1] = values[int(.99*len(values))]
        sDict[2] = values[int(.9*len(values))]
        sDict[3] = values[int(.8*len(values))]
        sDict[4] = values[int(.7*len(values))]
        sDict[5] = values[int(.6*len(values))]

        return sDict.copy()


################################################################################
################################################################################
