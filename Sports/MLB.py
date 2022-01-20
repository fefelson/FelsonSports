from copy import deepcopy
from datetime import date, datetime, timedelta

from .. import Environ as ENV
from ..DB import MLBDB
from ..Models import (DailyBoxScore, DailyFileManager, DailySchedule,
                        League, DailyMatchup, MLBPlayer, MLBReport, yId)
from ..Utils.SQL import getGDCmds


################################################################################
################################################################################


awayHome = ("away", "home")
awayHomeDict = dict([(label, {}) for label in ("all", "away", "home")])
teamOppDict = dict([(label, {}) for label in ("team", "opp")])
awayOppDict =  dict([(label, deepcopy(teamOppDict)) for label in ("all", "away", "home")])



batStatList = ("ab", "r", "bb", "h", "hr", "rbi", "sb", "tb", "so", "avg", "obp", "slg", "ops")
pitchStatList = ("w","l", "sv", "ip", "bba", "ha", "k", "hra", "era", "whip", "k9")
gameLogList = ("at", "abrv", "teamSP", "oppSP", "result", "spread", "line", "money", "spreadOutcome", "moneyOutcome")
startGamingList = ("atsW", "atsL", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$")
teamStatList = ("g", "ab","r","bb", "h", "hr","rbi","sb","so","lob","avg", "obp", "ip","ra","era","whip","k9","hra")
teamGamingList = ("w", "l", "atsW", "atsL", "spread", "result", "spreadLine", "moneyLine", "ats$", "money$")


batterCmd = """
                SELECT player_id, first_name, last_name, bats
                    FROM players
                    WHERE player_id = ?
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
                WHERE bs.player_id = ?
            """


bullpenCmd = """
                SELECT player_id
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN bullpens AS bp
                        ON gd.game_id = bp.game_id
                    WHERE pitch_order > 1 AND team_id = ?
                    GROUP BY player_id
                    ORDER BY COUNT(player_id) DESC
                    LIMIT 7
                """


mlbGameLogCmd = """
                    SELECT (CASE WHEN gl.team_id = home_id THEN 'vs' ELSE 'at' END),
                            abrv, team.SP, opp.SP, result, spread, line, money, spread_outcome, money_outcome
                        FROM ( {0[gdCmd]} ) AS gd
                        INNER JOIN game_lines AS gl
                            ON gd.game_id = gl.game_id  {0[andGL]}
                        INNER JOIN teams
                            ON gl.opp_id = teams.team_id
                        INNER JOIN ( SELECT gd.game_id, team_id, last_name AS SP
                                        FROM ( {0[gdCmd]} ) AS gd
                                        INNER JOIN bullpens AS bp
                                            ON gd.game_id = bp.game_id
                                        INNER JOIN players AS p
                                            ON bp.player_id = p.player_id
                                        WHERE pitch_order = 1
                                    ) AS team
                            ON gl.game_id = team.game_id AND gl.team_id = team.team_id
                        INNER JOIN ( SELECT gd.game_id, team_id, last_name AS SP
                                        FROM ( {0[gdCmd]} ) AS gd
                                        INNER JOIN bullpens AS bp
                                            ON gd.game_id = bp.game_id
                                        INNER JOIN players AS p
                                            ON bp.player_id = p.player_id
                                        WHERE pitch_order = 1
                                    ) AS opp
                            ON gl.game_id = opp.game_id AND gl.opp_id = opp.team_id
                        WHERE gl.team_id = ?
                        ORDER BY gl.game_id DESC
                """


mlbTeamCmd = """
            SELECT COUNT(ts.team_id), SUM(ab), SUM(r), SUM(bb), SUM(h), SUM(hr), SUM(rbi), SUM(sb), SUM(so),
                    SUM(lob), (SUM(h)*1.0)/SUM(ab) AS ba, ((SUM(bb)+SUM(h))*1.0)/((SUM(ab)+SUM(bb))*1.0) AS obp,
                    SUM(ip), SUM(ra), (SUM(er)*9.0)/SUM(ip), (SUM(bba)+SUM(ha))/SUM(ip),
                    (SUM(k)*9.0)/SUM(ip), SUM(hra)
                FROM ( {0[gdCmd]} ) AS gd
                INNER JOIN team_stats AS ts
                    ON gd.game_id = ts.game_id {0[andTS]}
                WHERE ts.{0[team]}_id = ?
            """


mlbTeamGameCmd = """
                SELECT SUM((CASE WHEN gl.team_id = winner_id THEN 1 ELSE 0 END)) AS wins,
                        SUM((CASE WHEN gl.team_id = loser_id THEN 1 ELSE 0 END)) AS loses,
                        SUM((CASE spread_outcome WHEN 1 THEN 1 ELSE 0 END)) ats_wins,
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
                    WHERE gl.{0[team]}_id = ?
                """


pastLineupCmd = """
                SELECT player_id, pos
                    FROM lineups AS l
                    INNER JOIN ( SELECT game_id, team_id
                                    FROM games AS g
                                    INNER JOIN teams AS t
                                        ON g.home_id = t.team_id OR g.away_id = t.team_id
                                    WHERE team_id = ?
                                    ORDER BY game_id DESC
                                    LIMIT 1) AS gd
                        ON l.game_id = gd.game_id AND l.team_id = gd.team_id
                    WHERE sub_order = 1
                    ORDER BY batt_order
                """


pitcherStatsCmd = """
                SELECT SUM(w), SUM(l), SUM(sv), SUM(ip), SUM(bba), SUM(ha), SUM(k), SUM(hra),
                        (SUM(er)*9.0)/SUM(ip), (SUM(bba)+SUM(ha))/SUM(ip), (SUM(k)*9)/SUM(ip)
                    FROM ( {0[gdCmd]} ) AS gd
                    INNER JOIN pitcher_stats AS ps
                        ON gd.game_id = ps.game_id {0[andPS]}
                    WHERE player_id = ?
                """


starterCmd = """
                SELECT player_id, first_name, last_name, throws
                    FROM players
                    WHERE player_id = ?
            """


starterGameCmd = """
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
                        ON gl.game_id = bp.game_id AND bp.team_id = gl.{0[team]}_id
                    WHERE pitch_order = 1 AND player_id = ?
                """


teamCmd = """
            SELECT team_id, abrv, first_name, last_name
                FROM teams
                WHERE team_id = ?
        """


vsBPCmd = """
            SELECT COUNT(ab_result_id)-IFNULL(bb.total,0), IFNULL(hrs.total,0), IFNULL(hits.total, 0)/((1.0*COUNT(ab.pitcher_id)-IFNULL(bb.total,0))), (IFNULL(hits.total, 0)*1.0)/(COUNT(ab.pitcher_id)) + (IFNULL(hits.total, 0)+ (IFNULL(dbls.total, 0)*1.0) + (IFNULL(tpls.total, 0)*2.0) + (IFNULL(hrs.total, 0)*3.0))/COUNT(ab.pitcher_id)
                FROM ab_results AS ab
                INNER JOIN bullpens AS bp
                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                INNER JOIN ( {0[gdCmd]} ) AS gd
                    ON ab.game_id = gd.game_id {0[andGD]}
                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id IN {0[pitcherId]} AND ab_type_id IN (2,6,8,15)
                                GROUP BY ab.batter_id
                            ) AS hits
                    ON ab.batter_id = hits.batter_id


                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id IN {0[pitcherId]} AND ab_type_id = 6
                                GROUP BY ab.batter_id
                            ) AS dbls
                    ON ab.batter_id = dbls.batter_id

                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id IN {0[pitcherId]} AND ab_type_id = 15
                                GROUP BY ab.batter_id
                            ) AS tpls
                    ON ab.batter_id = tpls.batter_id

                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN pitches
                                    ON ab.pitch_id = pitches.pitch_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id IN {0[pitcherId]} AND ab_type_id = 8
                                GROUP BY ab.batter_id
                            ) AS hrs
                    ON ab.batter_id = hrs.batter_id


                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id IN {0[pitcherId]} AND ab_type_id = 4
                                GROUP BY ab.batter_id
                            ) AS bb
                    ON ab.batter_id = bb.batter_id

                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id IN {0[pitcherId]}
                """


vsSPCmd = """
            SELECT COUNT(ab_result_id)-IFNULL(bb.total,0), IFNULL(hrs.total,0), IFNULL(hits.total, 0)/((1.0*COUNT(ab.pitcher_id)-IFNULL(bb.total,0))), (IFNULL(hits.total, 0)*1.0)/(COUNT(ab.pitcher_id)) + (IFNULL(hits.total, 0)+ (IFNULL(dbls.total, 0)*1.0) + (IFNULL(tpls.total, 0)*2.0) + (IFNULL(hrs.total, 0)*3.0))/COUNT(ab.pitcher_id)
                FROM ab_results AS ab
                INNER JOIN bullpens AS bp
                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                INNER JOIN ( {0[gdCmd]} ) AS gd
                    ON ab.game_id = gd.game_id {0[andGD]}
                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id IN (2,6,8,15)
                                GROUP BY ab.batter_id
                            ) AS hits
                    ON ab.batter_id = hits.batter_id


                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 6
                                GROUP BY ab.batter_id
                            ) AS dbls
                    ON ab.batter_id = dbls.batter_id

                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 15
                                GROUP BY ab.batter_id
                            ) AS tpls
                    ON ab.batter_id = tpls.batter_id

                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN pitches
                                    ON ab.pitch_id = pitches.pitch_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 8
                                GROUP BY ab.batter_id
                            ) AS hrs
                    ON ab.batter_id = hrs.batter_id


                LEFT JOIN ( SELECT ab.batter_id, COUNT(ab.batter_id) AS total
                                FROM ab_results AS ab
                                INNER JOIN bullpens AS bp
                                    ON ab.game_id = bp.game_id AND ab.pitcher_id = bp.player_id
                                INNER JOIN ( {0[gdCmd]} ) AS gd
                                    ON ab.game_id = gd.game_id {0[andGD]}
                                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]} AND ab_type_id = 4
                                GROUP BY ab.batter_id
                            ) AS bb
                    ON ab.batter_id = bb.batter_id

                WHERE ab.batter_id = {0[batterId]} AND ab.pitcher_id = {0[pitcherId]}
                """


################################################################################
################################################################################

class MLBMatchup(DailyMatchup):



    _info =  {"gameId": -1,
                "gameTime": None,
                "leagueId": "mlb",

                "homeId": -1,
                "awayId": -1,
                "url": None,
                "season": -1,
                "week": -1,
                "seasonPhase": -1,
                "starters": {"away":None, "home":None},
                "lineups": {"away":[], "home":[]},
                "players": {"away":[], "home":[]},
                "odds":[],
                "injuries":[],
                "data":{
                            "gameLog": {"away":{}, "home":{}},
                            "teams": {"away":{}, "home":{}},
                            "starters": {"away":{}, "home":{}},
                            "lineups": {"away":[], "home":[]},
                            "bullpens":{"away":{}, "home":{}},
                        },
                "lastUpdate": str(datetime.today())
                }

    def __init__(self, league, *args, **kwargs):
        super().__init__(league, *args, **kwargs)


    def parseData(self):

        stores = self.downloadItem()
        pageData = stores["PageStore"]["pageData"]
        game = stores["GamesStore"]["games"][pageData["entityId"]]

        setData = False

        if not self.info["gameId"] != -1:
            self.info["gameId"] = yId(game["gameid"])
            self.info["season"] = game.get("season", -1)
            self.info["week"] = game.get("week_number", -1)
            self.info["gameTime"] = game["start_time"]
            self.info["seasonPhase"] = game["season_phase_id"]
            self.info["url"] = self.url
            self.info["awayId"] = yId(game["away_team_id"])
            self.info["homeId"] = yId(game["home_team_id"])
            setData = True


        for hA in ("home", "away"):
            label = "{}Id".format(hA)
            try:
                players = [yId(p) for p in game["playersByTeam"]["{}.t.{}".format(self.info["leagueId"], self.info[label])]]
                if players != self.info["players"][hA]:
                    self.info["players"][hA] = players
                    setData = True
            except KeyError:
                pass

            try:
                starter = yId(game["byline"]["playersByType"]["{}_pitcher".format(hA)])
                if starter != self.info["starters"][hA]:
                    self.info["starters"][hA] = starter
                    setData = True
            except:
                pass

            lineup = []
            try:
                temp = game["lineups"]["{}_lineup".format(hA)]["B"]
                for batter in sorted(temp.values(), key=lambda x: x["order"]):
                    batterId = yId(batter["player_id"])
                    position = batter["position"]
                    lineup.append((batterId, position))
                if lineup != self.info["lineups"][hA]:
                    self.info["lineups"][hA] = lineup
                    setData = True
            except:
                for player in self.league.dbManager.fetchAll(pastLineupCmd, (self.info[label],)):
                    lineup.append(player)
                self.info["lineups"][hA] = lineup




        self.info["odds"].append(game.get("odds", {}))

        try:
            injury = [player["injury"] for player in stores["PlayersStore"]["players"].values() if player.get("injury", None)]
            self.info["injuries"] = []
            for player in injury:
                playerId = yId(player["player_id"])
                self.info["injury"].append((playerId, player["comment"], player["date"], player["type"]))
        except KeyError:
            pass

        if setData:
            self.matchupData()


    def matchupData(self):
        currentSeason = self.league.fileManager.info["currentSeason"]
        gdCmds = getGDCmds(int(currentSeason))
        timeFrame = ENV.tfBaseballChoices

        for hA in ("away", "home"):
            opp = "away" if hA == "home" else "home"

            newTeam = dict(zip(("teamId", "abrv", "firstName", "lastName"), self.league.dbManager.fetchOne(teamCmd, (self.info["{}Id".format(hA)],)) ))
            try:
                starter = dict(zip(("playerId", "firstName", "lastName", "throws"), self.league.dbManager.fetchOne(starterCmd, (self.info["starters"][hA],)) ))
            except TypeError:
                starter = {}


            lineup = []

            for playerId, pos in self.info["lineups"][hA]:
                try:
                    player = dict(zip(("playerId", "firstName", "lastName", "bats"), self.league.dbManager.fetchOne(batterCmd, (playerId,))))
                except:
                    player = {"playerId":playerId, "firstName": "N/A", "lastName": "N/A", "bats": "N"}
                player["pos"] = pos
                player["stats"] = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))
                lineup.append(deepcopy(player))


            bullpen = []
            oppBullpen = [x[0] for x in self.league.dbManager.fetchAll(bullpenCmd.format({"gdCmd":gdCmds["2Weeks"]}), (self.info["{}Id".format(opp)],))]

            for playerId in [x[0] for x in self.league.dbManager.fetchAll(bullpenCmd.format({"gdCmd":gdCmds["2Weeks"]}), (self.info["{}Id".format(hA)],))]:
                player = dict(zip(("playerId", "firstName", "lastName", "throws"), self.league.dbManager.fetchOne(starterCmd, (playerId,))))
                try:
                    player["stats"] = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))
                    bullpen.append(deepcopy(player))
                except:
                    pass

            teamStats = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))
            teamGaming = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))

            starterStats = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))
            starterGaming = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))
            gameLog = dict(zip(timeFrame, [deepcopy(awayHomeDict) for _ in timeFrame]))


            for tF in timeFrame:
                gdCmd = gdCmds[tF]

                for loc in ("all", hA):
                    andPS = "" if loc == "all" else "AND gd.{}_id = ps.team_id".format(hA)
                    andBS = "" if loc == "all" else "AND gd.{}_id = bs.team_id".format(hA)
                    andGL = "AND (gd.home_id = gl.team_id OR gd.away_id = gl.team_id)" if loc == "all" else "AND gd.{}_id = gl.team_id".format(hA)


                    for player in lineup:
                        player["stats"][tF][loc] = dict(zip(batStatList, self.league.dbManager.fetchOne(batPlayerCmd.format({"gdCmd":gdCmd, "andBS": andBS}), (player["playerId"],))))

                    for player in bullpen:
                        player["stats"][tF][loc] = dict(zip(pitchStatList, self.league.dbManager.fetchOne(pitcherStatsCmd.format({"gdCmd":gdCmd, "andPS": andPS}), (player["playerId"],))))
                        starterStats[tF][loc] = dict(zip(pitchStatList, self.league.dbManager.fetchOne(pitcherStatsCmd.format({"gdCmd":gdCmd, "andPS":andPS}), (self.info["starters"][hA],))))

                    gameLog[tF][loc] = [dict(zip(gameLogList, x)) for x in self.league.dbManager.fetchAll(mlbGameLogCmd.format({"gdCmd":gdCmd, "andGL":andGL}), (self.info["{}Id".format(hA)],))]

                    teamDict = {}
                    startDict = {}
                    for tO in ("team", "opp"):
                        andTS = "AND (gd.home_id = ts.{0}_id OR gd.away_id = ts.{0}_id)".format(tO) if loc == "all" else "AND gd.{}_id = ts.{}_id".format(hA, tO)

                        andGL = "" if loc == "all" else "AND gd.{}_id = gl.{}_id".format(hA, tO)
                        teamDict[tO] = dict(zip(teamGamingList, self.league.dbManager.fetchOne(mlbTeamGameCmd.format({"gdCmd":gdCmd, "andGL":andGL, "team": tO}), (self.info["{}Id".format(hA)],)) ))
                        startDict[tO] = dict(zip(startGamingList, self.league.dbManager.fetchOne(starterGameCmd.format({"gdCmd":gdCmd, "andGL":andGL, "team": tO}), (self.info["starters"][hA],)) ))
                        teamStats[tF][loc][tO] = dict(zip(teamStatList, self.league.dbManager.fetchOne(mlbTeamCmd.format({"gdCmd":gdCmd, "andTS":andTS, "team":tO}), (self.info["{}Id".format(hA)],))))

                    teamGaming[tF][loc] = deepcopy(teamDict)
                    starterGaming[tF][loc] = deepcopy(startDict)

            for player in lineup:
                try:
                    player["vsSP"] = dict(zip(("ab", "hr", "avg", "ops"), self.league.dbManager.fetchOne(vsSPCmd.format({"gdCmd":"SELECT game_id, home_id, away_id, winner_id, loser_id FROM games", "andGD":"", "batterId": player["playerId"], "pitcherId":self.info["starters"][opp]}))))
                except:
                    player["vsSP"] = {}

            for player in lineup:
                print(self.league.dbManager.fetchOne(vsBPCmd.format({"gdCmd":"SELECT game_id, home_id, away_id, winner_id, loser_id FROM games", "andGD":"", "batterId": player["playerId"], "pitcherId":str(tuple(oppBullpen))})))
                player["vsBP"] = dict(zip(("ab", "hr", "avg", "ops"), self.league.dbManager.fetchOne(vsBPCmd.format({"gdCmd":"SELECT game_id, home_id, away_id, winner_id, loser_id FROM games", "andGD":"", "batterId": player["playerId"], "pitcherId":str(tuple(oppBullpen))}))))


            newTeam["stats"] = deepcopy(teamStats)
            newTeam["gaming"] = deepcopy(teamGaming)
            newTeam["gameLog"] = deepcopy(gameLog)

            starter["stats"] = deepcopy(starterStats)

            starter["gaming"] = deepcopy(starterGaming)

            self.info["data"]["teams"][hA] = deepcopy(newTeam)
            self.info["data"]["starters"][hA] = deepcopy(starter)
            self.info["data"]["lineups"][hA] = deepcopy(lineup)
            self.info["data"]["bullpens"][hA] = deepcopy(bullpen)


################################################################################
################################################################################



class MLB(League):

    _boxScore = DailyBoxScore
    _dbManager = MLBDB
    _fileManager = DailyFileManager
    _info = {
                "leagueId": "mlb",
                "slugId": "mlb",
                "lastUpdate": "2021-11-04",
                "currentSeason": "2021",
                "startDate": "2021-03-01",
                "playoffs": "2021-10-04",
                "endDate": "2021-11-04",
                "allStar": "2021-07-13"
            }
    _matchup = MLBMatchup
    _player = MLBPlayer
    _reportManager = MLBReport
    _schedule = DailySchedule



    def __init__(self, *args, **kwargs):
        print("MLB constructor")
        super().__init__(*args, **kwargs)
