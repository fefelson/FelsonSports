import MLBProjections.MLBProjections.DB.MLB as DB
import MLBProjections.MLBProjections.Environ as ENV
from matplotlib import pyplot as plt
from pprint import pprint
import numpy
import scipy.stats as sci
import datetime
import csv
import os
import json
import copy
import re
import wx
from wx.lib.agw.shapedbutton import SToggleButton
import wx.lib.inspection


oneMonth = datetime.date.today()- datetime.timedelta(30)
twoWeeks = datetime.date.today()- datetime.timedelta(14)
threeMonths = datetime.date.today()- datetime.timedelta(90)


gameDateCmd = """
                SELECT game_id, home_id, away_id
                    FROM games
                    {}
                """

def getGDCmd(startDate=None, endDate=None, season=None):
    whereCmd = ""
##    print(startDate)
    if season:
        whereCmd = "WHERE season = {}".format(season)
    elif not startDate and not endDate:
        pass
    elif not endDate:
        whereCmd = "WHERE season = {} AND game_date >= {}.{}".format(*str(startDate).split("-"))
    elif not startDate:
        whereCmd = "WHERE game_date <= {}.{}".format(*str(endDate).split("-")[1:])
    else:
        whereCmd = "WHERE game_date >= {}.{} AND game_date <= {}.{}".format(*str(startDate).split("-")[1:], *str(endDate).split("-")[1:])
    return gameDateCmd.format(whereCmd)


scoreCmd = """
            SELECT game_id, team_id, opp_id, player_id, value * {0[multiply]} AS score
                FROM player_stats
                WHERE stat_id = {0[stat]}{0[andPlayerCmd]}
            """


valueCmd = """
            SELECT game_id, team_id, opp_id, player_id, value
                FROM player_stats
                WHERE stat_id = {0[stat]}{0[andPlayerCmd]}
            """


batResultCmd = """
                    SELECT game_id, batter_id AS player_id, pitcher_id, COUNT(batter_id) AS total
                        FROM ab_results
                        WHERE ab_results.ab_type_id = {0[abId]} {0[andPlayerCmd]}
                        GROUP BY game_id, player_id, pitcher_id
                """

pitchResultCmd = """
                    SELECT game_id, pitcher_id AS player_id, batter_id, COUNT(pitcher_id) AS total
                        FROM ab_results
                        WHERE ab_type_id = {0[abId]} {0[andPlayerCmd]}
                        GROUP BY game_id, player_id, batter_id
                """


abResultCmd = """
                    SELECT game_id, batter_id AS player_id, pitcher_id, COUNT(batter_id) AS total
                        FROM ab_results
                        INNER JOIN (SELECT ab_type_id FROM ab_types WHERE is_ab = 1) AS ab_types
                            ON ab_results.ab_type_id = ab_types.ab_type_id
                          {0[whrPlayerCmd]}
                        GROUP BY game_id, player_id, pitcher_id
                """

hResultCmd = """
                    SELECT game_id, batter_id AS player_id, pitcher_id, COUNT(batter_id) AS total
                        FROM ab_results
                        INNER JOIN (SELECT ab_type_id FROM ab_types WHERE is_hit = 1) AS ab_types
                            ON ab_results.ab_type_id = ab_types.ab_type_id
                          {0[whrPlayerCmd]}
                        GROUP BY game_id, player_id, pitcher_id
                """









def setScoreCmd(multiply, stat):
    return scoreCmd.format({"multiply": multiply, "stat": stat, "andPlayerCmd":"{0[andPlayerCmd]}"})


def setValueCmd(stat):
    return valueCmd.format({"stat": stat, "andPlayerCmd":"{0[andPlayerCmd]}"})

def setResultCmd(abId):
    return batResultCmd.format({"abId": abId, "whrPlayerCmd":"{0[whrPlayerCmd]}", "andPlayerCmd":"{0[andPlayerCmd]}"})

def setPitcherResultCmd(abId):
    return pitchResultCmd.format({"abId": abId, "whrPlayerCmd":"{0[whrPlayerCmd]}", "andPlayerCmd":"{0[andPlayerCmd]}"})



singScoreCmd = setScoreCmd(3,15)
dblScoreCmd = setScoreCmd(5,5)
tplScoreCmd = setScoreCmd(8,6)
hrScoreCmd = setScoreCmd(10,7)
rbiScoreCmd = setScoreCmd(2,8)
rScoreCmd = setScoreCmd(2,3)
bbScoreCmd = setScoreCmd(2,14)
hbpScoreCmd = setScoreCmd(2,9)
sbScoreCmd = setScoreCmd(5,12)
ipScoreCmd = setScoreCmd(2.25,139)
wScoreCmd = setScoreCmd(4,101)
kScoreCmd = setScoreCmd(2,121)
erScoreCmd = setScoreCmd(-2,114)
haScoreCmd = setScoreCmd(-.6,111)
bbaScoreCmd = setScoreCmd(-.6,118)
hbpaScoreCmd = setScoreCmd(-.6,119)




ipValueCmd = setValueCmd(139)
wValueCmd = setValueCmd(101)
kValueCmd = setValueCmd(121)
erValueCmd = setValueCmd(114)
hValueCmd = setValueCmd(4)
singValueCmd = setValueCmd(15)
dblValueCmd = setValueCmd(5)
tplValueCmd = setValueCmd(6)
hrValueCmd = setValueCmd(7)
sbValueCmd = setValueCmd(12)
abValueCmd = setValueCmd(2)
rbiValueCmd = setValueCmd(8)
rValueCmd = setValueCmd(3)
bbValueCmd = setValueCmd(14)
haValueCmd = setValueCmd(111)
bbaValueCmd = setValueCmd(118)
paValueCmd = setValueCmd(1)
hraValueCmd = setValueCmd(115)


hrResultCmd = setResultCmd(8)
hraResultCmd = setPitcherResultCmd(8)
kResultCmd = setResultCmd(1)
bbResultCmd = setResultCmd(4)
dblResultCmd = setResultCmd(6)
tplResultCmd = setResultCmd(15)
singResultCmd = setResultCmd(2)
soResultCmd = setResultCmd(1)
#abResultCmd is above
#hResultCmd is above

def getBatItemCmd(itemCmd):
    return batItemCmd.format({"itemCmd":itemCmd, "gdCmd":"{0[gdCmd]}", "whrCmd":"{0[whrCmd]}"})

def getBatItemSideCmd(itemCmd):
    return batItemSideCmd.format({"itemCmd":itemCmd, "gdCmd":"{0[gdCmd]}", "whrCmd":"{0[whrCmd]}"})


batItemCmd = """
                SELECT SUM(a.total)
                    FROM ( {0[itemCmd]} ) AS a
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON a.game_id = gd.game_id
                    {0[whrCmd]}
            """

batItemSideCmd = """
                    SELECT SUM(a.total)
                        FROM ( {0[itemCmd]} ) AS a
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON a.game_id = gd.game_id
                        INNER JOIN pro_players AS pp
                            ON a.pitcher_id = pp.player_id
                        {0[whrCmd]}
                    """


batScoreCmd = """
                SELECT sing.game_id,
                        sing.player_id,
                        sing.team_id,
                        sing.opp_id,
                        sing.score + dbl.score + tpl.score + hr.score + r.score + rbi.score + bb.score + hbp.score + sb.score AS total
                    FROM ( {0[singScoreCmd]} ) AS sing
                    INNER JOIN ( {0[dblScoreCmd]} ) AS dbl
                        ON sing.player_id = dbl.player_id AND sing.game_id = dbl.game_id
                    INNER JOIN ( {0[tplScoreCmd]} ) AS tpl
                        ON sing.player_id = tpl.player_id AND sing.game_id = tpl.game_id
                    INNER JOIN ( {0[hrScoreCmd]} ) AS hr
                        ON sing.player_id = hr.player_id AND sing.game_id = hr.game_id
                    INNER JOIN ( {0[rbiScoreCmd]} ) AS rbi
                        ON sing.player_id = rbi.player_id AND sing.game_id = rbi.game_id
                    INNER JOIN ( {0[rScoreCmd]} ) AS r
                        ON sing.player_id = r.player_id AND sing.game_id = r.game_id
                    INNER JOIN ( {0[bbScoreCmd]} ) AS bb
                        ON sing.player_id = bb.player_id AND sing.game_id = bb.game_id
                    INNER JOIN ( {0[hbpScoreCmd]} ) AS hbp
                        ON sing.player_id = hbp.player_id AND sing.game_id = hbp.game_id
                    INNER JOIN ( {0[sbScoreCmd]} ) AS sb
                        ON sing.player_id = sb.player_id AND sing.game_id = sb.game_id
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON sing.game_id = gd.game_id
                    INNER JOIN pro_players AS pp
                        ON sing.player_id = pp.player_id
                    {0[whrPlayerCmd]}
            """.format({"singScoreCmd":singScoreCmd, "dblScoreCmd":dblScoreCmd, "tplScoreCmd":tplScoreCmd, "hrScoreCmd":hrScoreCmd,
                        "rbiScoreCmd":rbiScoreCmd, "rScoreCmd":rScoreCmd, "bbScoreCmd":bbScoreCmd,
                        "hbpScoreCmd":hbpScoreCmd, "sbScoreCmd":sbScoreCmd, "gdCmd":"{0[gdCmd]}", "whrPlayerCmd": "{0[whrPlayerCmd]}"})


pitchScoreCmd = """
                SELECT ip.game_id,
                        ip.player_id,
                        ip.team_id,
                        ip.opp_id,
                        ip.score + w.score + k.score + er.score + h.score + bb.score + hbp.score AS total
                    FROM ( {0[ipCmd]} ) AS ip
                    INNER JOIN ( {0[kCmd]} ) AS k
                        ON ip.player_id = k.player_id AND ip.game_id = k.game_id
                    INNER JOIN ( {0[erCmd]} ) AS er
                        ON ip.player_id = er.player_id AND ip.game_id = er.game_id
                    INNER JOIN ( {0[hCmd]} ) AS h
                        ON ip.player_id = h.player_id AND ip.game_id = h.game_id
                    INNER JOIN ( {0[bbCmd]} ) AS bb
                        ON ip.player_id = bb.player_id AND ip.game_id = bb.game_id
                    INNER JOIN ( {0[hbpCmd]} ) AS hbp
                        ON ip.player_id = hbp.player_id AND ip.game_id = hbp.game_id
                   INNER JOIN ( {0[wCmd]} ) AS w
                        ON ip.player_id = w.player_id AND ip.game_id = w.game_id
                   INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON ip.game_id = gd.game_id
                    INNER JOIN pro_players AS pp
                        ON ip.player_id = pp.player_id
                    {0[whrPlayerCmd]}
            """.format({"ipCmd": ipScoreCmd, "wCmd":wScoreCmd, "whrPlayerCmd": "{0[whrPlayerCmd]}", "kCmd": kScoreCmd, "erCmd": erScoreCmd, "hCmd": haScoreCmd, "bbCmd":bbaScoreCmd, "hbpCmd":hbpaScoreCmd, "gdCmd":"{0[gdCmd]}"})


pitchReviewCmd = """
                    SELECT SUM(ip.value),
                            SUM(w.value),
                            (SUM(er.value) * 9)/SUM(ip.value),
                            (SUM(bba.value) + SUM(ha.value))/SUM(ip.value),
                            (SUM(k.value) * 9)/SUM(ip.value)
                        FROM ( {0[ipCmd]} ) AS ip
                        INNER JOIN ( {0[kCmd]} ) AS k
                            ON ip.player_id = k.player_id AND ip.game_id = k.game_id
                        INNER JOIN ( {0[wCmd]} ) AS w
                            ON ip.player_id = w.player_id AND ip.game_id = w.game_id
                        INNER JOIN ( {0[erCmd]} ) AS er
                            ON ip.player_id = er.player_id AND ip.game_id = er.game_id
                        INNER JOIN ( {0[hCmd]} ) AS ha
                            ON ip.player_id = ha.player_id AND ip.game_id = ha.game_id
                        INNER JOIN ( {0[bbCmd]} ) AS bba
                            ON ip.player_id = bba.player_id AND ip.game_id = bba.game_id
                        INNER JOIN pro_players AS pp
                            ON ip.player_id = pp.player_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ip.game_id = gd.game_id
                        {0[whrPlayerCmd]}
                    """.format({"ipCmd": ipValueCmd, "wCmd":wValueCmd, "whrPlayerCmd": "{0[whrPlayerCmd]}", "kCmd": kValueCmd, "erCmd": erValueCmd, "hCmd": haValueCmd, "bbCmd":bbaValueCmd, "gdCmd":"{0[gdCmd]}"})



batReviewCmd = """
                SELECT COUNT(gd.game_id),
                        SUM(ab.value),
                        SUM(r.value),
                        SUM(bb.value),
                        SUM(h.value),
                        SUM(hr.value),
                        SUM(rbi.value),
                        SUM(sb.value),
                        (SUM(h.value) + SUM(dbl.value) + (SUM(tpl.value)*2) + (SUM(hr.value)*3)) AS tb
                    FROM pro_players AS pp
                    INNER JOIN ( {0[abCmd]} ) AS ab
                        ON pp.player_id = ab.player_id
                    INNER JOIN ( {0[dblCmd]} ) AS dbl
                        ON ab.player_id = dbl.player_id AND ab.game_id = dbl.game_id
                    INNER JOIN ( {0[hCmd]} ) AS h
                        ON ab.player_id = h.player_id AND ab.game_id = h.game_id
                    INNER JOIN ( {0[tplCmd]} ) AS tpl
                        ON ab.player_id = tpl.player_id AND ab.game_id = tpl.game_id
                    INNER JOIN ( {0[hrCmd]} ) AS hr
                        ON ab.player_id = hr.player_id AND ab.game_id = hr.game_id
                    INNER JOIN ( {0[sbCmd]} ) AS sb
                        ON ab.player_id = sb.player_id AND ab.game_id = sb.game_id
                    INNER JOIN ( {0[bbCmd]} ) AS bb
                        ON ab.player_id = bb.player_id AND ab.game_id = bb.game_id
                    INNER JOIN ( {0[rCmd]} ) AS r
                        ON ab.player_id = r.player_id AND ab.game_id = r.game_id
                    INNER JOIN ( {0[rbiCmd]} ) AS rbi
                        ON ab.player_id = rbi.player_id AND ab.game_id = rbi.game_id
                    INNER JOIN ( {0[gdCmd]} ) AS gd
                        ON ab.game_id = gd.game_id
                    {0[whrCmd]}
            """.format({"bbCmd": bbValueCmd, "abCmd": abValueCmd, "dblCmd": dblValueCmd, "hCmd":hValueCmd,
                        "tplCmd": tplValueCmd, "hrCmd": hrValueCmd, "sbCmd": sbValueCmd, "whrPlayerCmd":"{0[whrPlayerCmd]}",
                        "gdCmd":"{0[gdCmd]}", "whrCmd":"{0[whrCmd]}", "rCmd": rValueCmd, "rbiCmd": rbiValueCmd})



pitchVsCmd = """
                    SELECT SUM(ip.value),
                            SUM(w.value),
                            (SUM(er.value) * 9)/SUM(ip.value),
                            (SUM(bba.value) + SUM(ha.value))/SUM(ip.value),
                            (SUM(k.value) * 9)/SUM(ip.value)
                        FROM ( {0[ipCmd]} ) AS ip
                        INNER JOIN ( {0[kCmd]} ) AS k
                            ON ip.player_id = k.player_id AND ip.game_id = k.game_id
                        INNER JOIN ( {0[wCmd]} ) AS w
                            ON ip.player_id = w.player_id AND ip.game_id = w.game_id
                        INNER JOIN ( {0[erCmd]} ) AS er
                            ON ip.player_id = er.player_id AND ip.game_id = er.game_id
                        INNER JOIN ( {0[hCmd]} ) AS ha
                            ON ip.player_id = ha.player_id AND ip.game_id = ha.game_id
                        INNER JOIN ( {0[bbCmd]} ) AS bba
                            ON ip.player_id = bba.player_id AND ip.game_id = bba.game_id
                        INNER JOIN pro_players AS pp
                            ON ip.player_id = pp.player_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ip.game_id = gd.game_id
                        {0[whrPlayerCmd]} AND ip.opp_id = ?
                    """.format({"ipCmd": ipValueCmd, "wCmd":wValueCmd, "whrPlayerCmd": "{0[whrPlayerCmd]}", "kCmd": kValueCmd, "erCmd": erValueCmd, "hCmd": haValueCmd, "bbCmd":bbaValueCmd, "gdCmd":"{0[gdCmd]}"})



pitchGameCmd = """
                    SELECT ip.game_id,
                            w.value,
                            ip.value,
                            ha.value,
                            er.value,
                            bba.value,
                            k.value
                        FROM ( {0[ipCmd]} ) AS ip
                        INNER JOIN ( {0[wCmd]} ) AS w
                            ON ip.player_id = w.player_id AND ip.game_id = w.game_id
                        INNER JOIN ( {0[erCmd]} ) AS er
                            ON ip.player_id = er.player_id AND ip.game_id = er.game_id
                        INNER JOIN ( {0[hCmd]} ) AS ha
                            ON ip.player_id = ha.player_id AND ip.game_id = ha.game_id
                        INNER JOIN ( {0[bbCmd]} ) AS bba
                            ON ip.player_id = bba.player_id AND ip.game_id = bba.game_id
                        INNER JOIN ( {0[kCmd]} ) AS k
                            ON ip.player_id = k.player_id AND ip.game_id = k.game_id
                        INNER JOIN pro_players AS pp
                            ON ip.player_id = pp.player_id
                        INNER JOIN ( {0[gdCmd]} ) AS gd
                            ON ip.game_id = gd.game_id
                        {0[whrPlayerCmd]}
                        ORDER BY ip.game_id DESC
                    """.format({"ipCmd": ipValueCmd, "wCmd":wValueCmd, "whrPlayerCmd": "{0[whrPlayerCmd]}", "kCmd": kValueCmd, "erCmd": erValueCmd, "hCmd": haValueCmd, "bbCmd":bbaValueCmd, "gdCmd":"{0[gdCmd]}"})
                          


pitchAvgScoreCmd = """
                        SELECT COUNT(ps.game_id), AVG(total)
                            FROM ( {0[psCmd]} ) AS ps
                            INNER JOIN bullpens
                                ON ps.game_id = bullpens.game_id AND ps.player_id = bullpens.player_id
                            {0[whrCmd]}
                    """.format({"psCmd":pitchScoreCmd, "whrCmd": "{0[whrCmd]}"})


pitchThrowsScoreCmd = """
                        SELECT COUNT(ps.game_id), AVG(total)
                            FROM ( {0[psCmd]} ) AS ps
                            INNER JOIN bullpens
                                ON ps.game_id = bullpens.game_id AND ps.player_id = bullpens.player_id
                            INNER JOIN pro_players
                                ON ps.player_id = pro_players.player_id
                            {0[whrCmd]}
                    """.format({"psCmd":pitchScoreCmd, "whrCmd": "{0[whrCmd]}"})


pitchCountCmd = """
                SELECT COUNT(player_id)
                    FROM ( {0[psCmd]} ) AS ps
                    {0[whrCmd]}
                """.format({"psCmd":pitchScoreCmd, "whrCmd": "{0[whrCmd]}"})


batAvgScoreCmd = """
                        SELECT COUNT(bs.game_id), AVG(total)
                            FROM ( {0[bsCmd]} ) AS bs
                            {0[whrCmd]}
                    """.format({"bsCmd":batScoreCmd, "whrCmd": "{0[whrCmd]}"})



batThrowsScoreCmd = """
                        SELECT COUNT(bs.game_id), AVG(total)
                            FROM ( {0[bsCmd]} ) AS bs
                            INNER JOIN ( SELECT game_id, team_id, opp_id, player_id FROM bullpens WHERE pitch_order = 1)
                                AS bp
                                ON bs.game_id = bp.game_id AND bs.team_id = bp.opp_id 
                            INNER JOIN pro_players
                                ON bp.player_id = pro_players.player_id
                            {0[whrCmd]}
                    """.format({"bsCmd":batScoreCmd, "whrCmd": "{0[whrCmd]}"})




batCountCmd = """
                SELECT COUNT(player_id)
                    FROM ( {0[bsCmd]} ) AS bs
                    {0[whrCmd]}
                """.format({"bsCmd":batScoreCmd, "whrCmd": "{0[whrCmd]}"})






class Pitcher:

    _player = {
                "playerType": "pitcher",
                "gameId": -1,
                "playerId": -1,
                "firstName": "N/A",
                "lastName": "N/A",
                "pos": ["P",],
                "throws": "N/A",
                "price": -1,
                "pts": {"career": {}, "season":{}, "month":{}, "team":{}},
                "stats": {"career":{}, "season":{}, "month":{}, "team":{}},
                "pitches": {"mainPitch":{}, "secondPitch":{}, "kPitch":{}},
                "priceHistory": {}                
            }
                
                

    def __init__(self, gameId, model, opp, playerId):

        self.info = copy.deepcopy(self._player)
        self.info["gameId"] = gameId
        self.info["playerId"] = playerId
        self.info["throws"] = model.mlbDB.fetchItem("SELECT throws FROM pro_players WHERE player_id = ?", (playerId,))
        self.info["price"] = model.fanDB.fetchItem("SELECT price FROM dk_prices INNER JOIN dk_sheet_players ON dk_prices.dk_price_id = dk_sheet_players.dk_price_id INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id WHERE yahoo_id = ?", (playerId,))
        self.info["firstName"],  self.info["lastName"] = model.mlbDB.fetchOne("SELECT first_name, last_name FROM pro_players WHERE player_id = ?", (playerId,))
        try:
            self.info["stats"]["career"] = dict(zip(("ip","w","era","whip","k9"), model.mlbDB.fetchOne(pitchReviewCmd.format({"whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass
        try:
            self.info["stats"]["season"] = dict(zip(("ip","w","era","whip","k9"), model.mlbDB.fetchOne(pitchReviewCmd.format({"whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(season=2019)}))))
        except TypeError:
            pass
        try:
            self.info["stats"]["month"] = dict(zip(("ip","w","era","whip","k9"), model.mlbDB.fetchOne(pitchReviewCmd.format({"whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(startDate=oneMonth)}))))
        except TypeError:
            pass 
        try:
            self.info["stats"]["team"] = dict(zip(("ip","w","era","whip","k9"), model.mlbDB.fetchOne(pitchVsCmd.format({"whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}), (opp["teamId"],) )))
        except TypeError:
            pass

        try:
            self.info["pts"]["career"] = dict(zip(("games","pts"), model.mlbDB.fetchOne(pitchAvgScoreCmd.format({"whrCmd":"", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass
        try:
            self.info["pts"]["season"] = dict(zip(("games","pts"), model.mlbDB.fetchOne(pitchAvgScoreCmd.format({"whrCmd":"", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(season=2019)}))))
        except TypeError:
            pass
        try:
            self.info["pts"]["month"] = dict(zip(("games","pts"), model.mlbDB.fetchOne(pitchAvgScoreCmd.format({"whrCmd":"", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(startDate=oneMonth)}))))
        except TypeError:
            pass
        try:
            self.info["pts"]["team"] = dict(zip(("games","pts"), model.mlbDB.fetchOne(pitchAvgScoreCmd.format({"whrCmd":"WHERE ps.opp_id = "+str(opp["teamId"]), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass

        self.info["ptsVsAll"] = opp["ptsVsAll"]
        self.info["ptsVsThrow"] = opp["ptsVsThrow"]
                                              
        

    def __repr__(self):
        return "{}  {} {}".format(self.info["playerId"], self.info["firstName"], self.info["lastName"])


    

class Batter:

    _player = {
                "playerType": "batter",
                "gameId":-1,
                "playerId": -1,
                "firstName": "N/A",
                "lastName": "N/A",
                "pos": [],
                "bats": "N/A",
                "price": -1,
                "pts": {"career": {}, "season":{}, "month":{}, "team":{}},
                "ptsVsThrows": {"career": {}, "season":{}, "month":{}, "team":{}},
                "stats": {"career":{}, "season":{}, "month":{}, "team":{}},
                "statsVsThrows": {"career":{}, "season":{}, "month":{}},
                "statsVsPitcher": {"career":{}, "season":{}},
                "priceHistory": {}                
            }


    def __init__(self, gameId, model, opp, playerId):

        self.info = copy.deepcopy(self._player)
        self.info["gameId"] = gameId
        self.info["playerId"] = playerId
        self.info["bats"] = model.mlbDB.fetchItem("SELECT bats FROM pro_players WHERE player_id = ?", (playerId,))
        self.info["price"] = model.fanDB.fetchItem("SELECT price FROM dk_prices INNER JOIN dk_sheet_players ON dk_prices.dk_price_id = dk_sheet_players.dk_price_id INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id WHERE yahoo_id = ?", (playerId,))
        self.info["firstName"],  self.info["lastName"] = model.mlbDB.fetchOne("SELECT first_name, last_name FROM pro_players WHERE player_id = ?", (playerId,))
        self.info["pos"] = model.fanDB.fetchItem("SELECT pos FROM dk_prices INNER JOIN dk_sheet_players ON dk_prices.dk_price_id = dk_sheet_players.dk_price_id INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id WHERE yahoo_id = ?", (playerId,)).split(",")

        try:
            self.info["stats"]["career"] = dict(zip(("games","ab","r", "bb", "h", "hr", "rbi", "sb", "tb"), model.mlbDB.fetchOne(batReviewCmd.format({"whrCmd":" WHERE pp.player_id ="+str(playerId), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass
        try:
            self.info["stats"]["season"] = dict(zip(("games","ab","r", "bb", "h", "hr", "rbi", "sb", "tb"), model.mlbDB.fetchOne(batReviewCmd.format({"whrCmd":" WHERE pp.player_id ="+str(playerId), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(season=2019)}))))
        except TypeError:
            pass
        try:
            self.info["stats"]["month"] = dict(zip(("games","ab","r", "bb", "h", "hr", "rbi", "sb", "tb"), model.mlbDB.fetchOne(batReviewCmd.format({"whrCmd":" WHERE pp.player_id ="+str(playerId), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(startDate=oneMonth)}))))
        except TypeError:
            pass
        try:
            self.info["stats"]["team"] = dict(zip(("games","ab","r", "bb", "h", "hr", "rbi", "sb", "tb"), model.mlbDB.fetchOne(batReviewCmd.format({"whrCmd":" WHERE pp.player_id ="+str(playerId)+" AND ab.opp_id = ?", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}), (opp["teamId"],))))
        except TypeError:
            pass
        try:
            self.info["pts"]["career"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batAvgScoreCmd.format({"whrCmd":"WHERE player_id ="+str(playerId), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass
        try:
            self.info["pts"]["season"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batAvgScoreCmd.format({"whrCmd":"WHERE player_id ="+str(playerId), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(season=2019)}))))
        except TypeError:
            pass
        try:
            self.info["pts"]["month"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batAvgScoreCmd.format({"whrCmd":"WHERE player_id ="+str(playerId), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(startDate=oneMonth)}))))
        except TypeError:
            pass
        try:
            self.info["pts"]["team"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batAvgScoreCmd.format({"whrCmd":"WHERE player_id ="+str(playerId)+" AND opp_id = "+str(opp["teamId"]), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass

        try:
            self.info["ptsVsThrows"]["career"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batThrowsScoreCmd.format({"whrCmd":"WHERE bs.player_id ="+str(playerId) + " AND throws = '"+opp["throws"]+"'", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass
        try:
            self.info["ptsVsThrows"]["season"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batThrowsScoreCmd.format({"whrCmd":"WHERE bs.player_id ="+str(playerId) + " AND throws = '"+opp["throws"]+"'", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(season=2019)}))))
        except TypeError:
            pass
        try:
            self.info["ptsVsThrows"]["month"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batThrowsScoreCmd.format({"whrCmd":"WHERE bs.player_id ="+str(playerId) + " AND throws = '"+opp["throws"]+"'", "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd(startDate=oneMonth)}))))
        except TypeError:
            pass
        try:
            self.info["ptsVsThrows"]["team"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(batThrowsScoreCmd.format({"whrCmd":"WHERE bs.player_id ="+str(playerId) + " AND throws = '"+opp["throws"]+"' AND bs.opp_id = "+str(opp["teamId"]), "whrPlayerCmd":" WHERE pp.player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":getGDCmd()}))))
        except TypeError:
            pass

        for timeFrame, gdCmd in (("career",getGDCmd()), ("season", getGDCmd(season=2019)), ("month", getGDCmd(startDate=oneMonth))):
            for statAbrv, itemCmd in (("ab", abResultCmd), ("sing", singResultCmd), ("dbl", dblResultCmd), ("tpl", tplResultCmd), ("hr", hrResultCmd), ("so", soResultCmd)):
                if timeFrame in ("career", "season"):
                    try:
                        vsStat = model.mlbDB.fetchItem(getBatItemCmd(itemCmd).format({"whrCmd": "WHERE player_id = "+str(playerId)+" AND pitcher_id = "+str(opp["starter"]), "whrPlayerCmd":" WHERE player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":gdCmd}))
                    except TypeError:
                        vsStat = 0
                    vsStat = 0 if not vsStat else vsStat
                    self.info["statsVsPitcher"][timeFrame][statAbrv] = vsStat

                try:
                    throwStat = model.mlbDB.fetchItem(getBatItemSideCmd(itemCmd).format({"whrCmd": "WHERE a.player_id = "+str(playerId)+" AND throws = '"+str(opp["throws"])+"'", "whrPlayerCmd":" WHERE player_id ="+str(playerId), "andPlayerCmd":" AND player_id = "+str(playerId), "gdCmd":gdCmd}))
                except TypeError:
                    throwStat = 0
                throwStat = 0 if not throwStat else throwStat
                self.info["statsVsThrows"][timeFrame][statAbrv] = throwStat
        

    def __repr__(self):
        return "{}  {} {}".format(self.info["playerId"], self.info["firstName"], self.info["lastName"])


        




class Matchup:

    def __init__(self, model, info):

        self.teams = self.setTeams(model, info)
        self.players = []
        gameId = info["gameId"]
        for team, opp in ((self.teams["home"],self.teams["away"]),(self.teams["away"],self.teams["home"])):
            newPlayer = Pitcher(gameId, model, opp, team["starter"])
            print(newPlayer)
            self.players.append(newPlayer)
            for batterId in [batterId for batterId in team["lineup"] if batterId != team["starter"]]:
                newPlayer = Batter(gameId, model, opp, batterId)
                print(newPlayer)
                self.players.append(newPlayer)
            


    def setTeams(self, model, info):
        team = {
                "teamId": -1,
                "abrv": "N/A",
                "starter": -1,
                "throws": "N/A",
                "lineup": None,
                "ptsVsAll": {"season":{}, "month":{}},
                "ptsVsThrow": {"season":{}, "month":{}}
                }
        teams = {}
        for homeAway in ("home", "away"):
            # Dirty Hack ######################################
            try:
                oppHomeAway = "away" if homeAway == "home" else "home"
                oppId = info[oppHomeAway]["teamId"]
                oppSpId = info[oppHomeAway]["starter"]
                oppThrows = model.mlbDB.fetchItem("SELECT throws FROM pro_players WHERE player_id = ?", (oppSpId,))
            except TypeError:
                oppAbrv = model.mlbDB.fetchItem("SELECT abrv FROM pro_teams WHERE team_id = ?",(info[oppHomeAway]["teamId"],))
                oppThrows = input("{}".format(oppAbrv))
                                                  
            newTeam = team.copy()
            newTeam["teamId"] = info[homeAway]["teamId"]
            newTeam["abrv"] = model.mlbDB.fetchItem("SELECT abrv FROM pro_teams WHERE team_id = ?",(info[homeAway]["teamId"],))
            newTeam["starter"] = info[homeAway]["starter"]
            newTeam["lineup"] = [x[0] for x in info[homeAway]["lineup"]]
            newTeam["throws"] = model.mlbDB.fetchItem("SELECT throws FROM pro_players WHERE player_id = ?", (info[homeAway]["starter"],))

            try:
                newTeam["ptsVsAll"]["season"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(pitchAvgScoreCmd.format({"whrCmd":"WHERE pitch_order = 1 AND ps.opp_id = "+str(oppId), "whrPlayerCmd":"", "andPlayerCmd":"", "gdCmd":getGDCmd(season=2019)}))))
            except TypeError:
                pass
            try:
                newTeam["ptsVsAll"]["month"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(pitchAvgScoreCmd.format({"whrCmd":"WHERE pitch_order = 1 AND ps.opp_id = "+str(oppId), "whrPlayerCmd":"", "andPlayerCmd":"", "gdCmd":getGDCmd(startDate=oneMonth)}))))
            except TypeError:
                pass
            try:
                newTeam["ptsVsThrow"]["season"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(pitchThrowsScoreCmd.format({"whrCmd":"WHERE pitch_order = 1 AND throws = '"+oppThrows+"' AND ps.opp_id = "+str(oppId), "whrPlayerCmd":"", "andPlayerCmd":"", "gdCmd":getGDCmd(season=2019)}))))
            except TypeError:
                pass
            try:
                newTeam["ptsVsThrow"]["month"] = dict(zip(("games", "pts"), model.mlbDB.fetchOne(pitchThrowsScoreCmd.format({"whrCmd":"WHERE pitch_order = 1 AND throws = '"+oppThrows+"' AND ps.opp_id = "+str(oppId), "whrPlayerCmd":"", "andPlayerCmd":"", "gdCmd":getGDCmd(startDate=oneMonth)}))))
            except TypeError:
                pass

                       
            teams[homeAway] = newTeam

        return teams



    

class Model:

    def __init__(self):

        self.fanDB = DB.MLBDFS()
        self.fanDB.openDB()

        self.mlbDB = DB.MLBDatabase()
        self.mlbDB.openDB()

        sheetId = 8

        self.matchups = []
        
        gameIds = [x[0] for x in self.fanDB.fetchAll("SELECT game_id FROM dk_sheet_games WHERE dk_sheet_id = ?",(sheetId,))]
        gameDate = self.fanDB.fetchOne("SELECT game_date FROM dk_sheets WHERE dk_sheet_id = ?",(sheetId,))[0].split("/")
        gameDate = datetime.date(int(gameDate[-1]), int(gameDate[0]), int(gameDate[1]))
        for gameId in gameIds:
            with open(ENV.getPath("matchup", fileName=gameId, gameDate=gameDate)) as fileIn:
                self.matchups.append(Matchup(self, json.load(fileIn)))


    def __del__(self):
        self.fanDB.closeDB()
        self.mlbDB.closeDB()
        



class View(wx.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetSize((1000,700))

        # Panels
        self.mainPanel = wx.Panel(self)
        self.tickerPanel = wx.ScrolledWindow(self.mainPanel, style=wx.HSCROLL)
        self.tickerPanel.SetScrollbars(20, 20, 50, 50)
        self.tickerPanel.SetMinSize((800,200))
        self.tickerPanel.SetBackgroundColour(wx.GREEN)
        self.listPanel = wx.ScrolledWindow(self.mainPanel, style=wx.VSCROLL)
        self.listPanel.SetScrollbars(20, 20, 50, 50)
        self.listPanel.SetBackgroundColour(wx.RED)

        # Fonts


        # Widgets

        #   buttons
        self.allBttn = wx.Button(self.mainPanel, label="All")
        self.homeBttn = wx.Button(self.mainPanel, label="Home")
        self.awayBttn = wx.Button(self.mainPanel, label="Away")
        self.pBttn = wx.Button(self.mainPanel, label="P")
        self.bBttn = wx.Button(self.mainPanel, label="B")
        self.cBttn = wx.Button(self.mainPanel, label="C")
        self.fbBttn = wx.Button(self.mainPanel, label="1B")
        self.sbBttn = wx.Button(self.mainPanel, label="2B")
        self.tbBttn = wx.Button(self.mainPanel, label="3B")
        self.ssBttn = wx.Button(self.mainPanel, label="SS")
        self.ofBttn = wx.Button(self.mainPanel, label="OF")

        #   sliders
        self.highSlider = wx.Slider(self.mainPanel, value=13000, minValue=2000, maxValue=13000)
        self.lowSlider = wx.Slider(self.mainPanel, value=2000, minValue=2000, maxValue=13000)

        #   textCtrls
        self.highValue = wx.TextCtrl(self.mainPanel, value="13000", style=wx.TE_READONLY)
        self.lowValue = wx.TextCtrl(self.mainPanel, value="2000", style=wx.TE_READONLY)
        


        # Sizers
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.tickerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.listSizer = wx.BoxSizer(wx.VERTICAL)

        #   in mainSizer
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer = wx.BoxSizer(wx.VERTICAL)

        #   in buttonSizer
        self.allBttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.posBttnSizer = wx.GridSizer(2, 4, 5, 5)
        self.priceSizer = wx.BoxSizer(wx.VERTICAL)

        #   in priceSizer
        self.priceValueSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add items to priceValueSizer
        self.priceValueSizer.Add(self.lowValue)
        self.priceValueSizer.Add(wx.StaticText(self.mainPanel, label="- between -"))
        self.priceValueSizer.Add(self.highValue)

        # Add items to priceSizer
        self.priceSizer.Add(self.highSlider, 0, wx.EXPAND)
        self.priceSizer.Add(self.priceValueSizer)
        self.priceSizer.Add(self.lowSlider, 0, wx.EXPAND)

        # Add items to posBttnSizer
        self.posBttnSizer.Add(self.pBttn)
        self.posBttnSizer.Add(self.bBttn)
        self.posBttnSizer.Add(self.cBttn)
        self.posBttnSizer.Add(self.fbBttn)
        self.posBttnSizer.Add(self.sbBttn)
        self.posBttnSizer.Add(self.tbBttn)
        self.posBttnSizer.Add(self.ssBttn)
        self.posBttnSizer.Add(self.ofBttn)
        
        # Add items to allBttnSizer
        self.allBttnSizer.Add(self.allBttn)
        self.allBttnSizer.Add(self.homeBttn)
        self.allBttnSizer.Add(self.awayBttn)

        # Add items to buttonSizer
        self.buttonSizer.Add(self.allBttnSizer)
        self.buttonSizer.Add(self.posBttnSizer)
        self.buttonSizer.Add(self.priceSizer)

        # Add items to topSizer
        self.topSizer.Add(self.buttonSizer)
        self.topSizer.Add(self.tickerPanel, 1, wx.EXPAND | wx.LEFT, 20)

        # Add items to mainSizer
        self.mainSizer.Add(self.topSizer, 0, wx.EXPAND | wx.ALL, 20)
        self.mainSizer.Add(self.listPanel, 1, wx.EXPAND | wx.ALL, 20)

        # Set Sizer
        self.mainPanel.SetSizer(self.mainSizer)
        self.tickerPanel.SetSizer(self.tickerSizer)
        self.listPanel.SetSizer(self.listSizer)

        self.Layout()
        

        


class Controller:

    def __init__(self, model):

        self.model = model
        self.view = View(None)
        self.view.Show()

        
        



if __name__ == "__main__":
    app = wx.App()
    model = Model()
    controller = Controller(model)
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

    
