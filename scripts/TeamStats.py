bucketCmd = "SELECT num, bucket, stat_avg, stat_15, stat_85, stat_40, stat_60, stat_max, stat_min FROM item_totals AS totals WHERE proj_id = '{0[projId]} AND item_type = '{0[item]}' AND stat_id = '{0[statId]}' AND time_frame = '{0[timeFrame]}' AND home_away = '{0[homeAway]} AND item_id = ?"


class TeamStat:

    def __init__(self, statId, team):

        self.team = team
        self.statId = statId

        self.statProj = {}
        self.estTotal = {}


    def getJson(self):

        jsonDict = {"statId":self.statId,
                    "statProj":self.statProj,
                    "estTotal": self.estTotal}
        
        return jsonDict


    def getTotal(self, item):
        return self.estTotal[item]


    def addToTotal(self, item, value):
        self.estTotal[item] += value
        

    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = round(self.negotiate(formatting))
            

    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 2
        result = 0

        dFormatting = formatting.copy()
        dFormatting["proj_id"] = formatting["proj_id"]+"D"

        teamResult = db.curs.execute(bucketCmd.format(formatting), (self.team.teamId,)).fetchone()
        pprint(teamResult)
        raise AssertionError
##        oppDResult =  db.curs.execute(bucketCmd.format(dFormatting), (self.team.oppId,)).fetchone()
##        matchResults = db.curs.execute(bucketCmd.format(formatting)).fetchone()
##        simResults = setSimResults(formatting, teamResult, oppDResult)
##
##        if team.b2b:
##            b2bFormatting = formatting.copy()
##            b2bFormatting["proj_id"] = "b2b"
##            b2bResults = setB2bResults(formatting)
##        if team.opp.b2b:
##            b2bFormatting = formatting.copy()
##            b2bFormatting["proj_id"] = "b2bD"
##            b2bDResults = setB2bDResults(formatting)
##
##        if simResults[0]:
##            index = {"poor":3,"ok":5,"average":2,"good":6, "elite":4}.get(simResults[1], 2)
##            totals.append(simResults[index])
##
##        if teamResult[0]:
##            totals.append(teamResult[index])
##
##        if oppDResult[0]:
##            totals.append(oppDResult[index])
##
##        if matchResults[0]:
##            totals.append(matchResults[index])
##
##         
##        if b2bResults:
##            totals.append(b2bResults[index])
##
##
##        
##        if b2bDResults:
##            totals.append(b2bDResults[index])
##
##
##        if len(totals):
##            result = numpy.mean(totals)
##        return result



class TeamMins(TeamStat):

    def __init__(self, team):
        super().__init__("mins", team)


    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = 48.0*5




class TeamPoss(TeamStat):

    def __init__(self, team):
        super().__init__("poss", team)


class TeamTurnPer(TeamStat):

    def __init__(self, team):
        super().__init__("turn_per", team)


     def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = self.negotiate(formatting)


class TeamTurn(TeamStat):

    def __init__(self, team):
        super().__init__("turn", team)


     def setStat(self, formatting):
        label = formatting["label"]
        turnPer = self.team.teamStats["turn_per"][label]
        poss = self.team.teamStats["poss"][label]
        self.statProj[label] = round(poss * turnPer)

        
        

        

class TeamFoulsPer(TeamStat):

    def __init__(self, team):
        super().__init__("fouls_per", team)

    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = self.negotiate(formatting)


    


class TeamFouls(TeamStat):

    def __init__(self, team):
        super().__init__("fouls", team)


    def setStats(self):
        foulsPer = self.team.teamStats["fouls_per"]
        poss = self.team.matchup.getOpp(self).teamStats["poss"]

        self.seasonProj = poss.seasonProj * foulsPer.seasonProj
        self.monthProj = poss.monthProj * foulsPer.monthProj
        self.homeAwayProj = poss.homeAwayProj * foulsPer.homeAwayProj
        self.lineupProj = poss.lineupProj * foulsPer.lineupProj

        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)
        


class TeamFga(TeamStat):

    def __init__(self, team):
        super().__init__("fga", team)


    def setStats(self):
        turn = self.team.teamStats["turn"]
        poss = self.team.teamStats["poss"]

        self.seasonProj = poss.seasonProj - turn.seasonProj
        self.monthProj = poss.monthProj - turn.monthProj
        self.homeAwayProj = poss.homeAwayProj - turn.homeAwayProj
        self.lineupProj = poss.lineupProj - turn.lineupProj

        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)


class TeamFgm(TeamStat):

    def __init__(self, team):
        super().__init__("fgm", team)


    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = 0
        for player in chain(self.team.starters,self.team.bench):
            fgm = player.playerStats["fgm"].getStatAdj(label)
            try:
                self.statProj[label] += round(fgm)
            except TypeError:
                pass
            

class TeamFtm(TeamStat):

    def __init__(self, team):
        super().__init__("ftm", team)


    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = 0
        for player in chain(self.team.starters,self.team.bench):
            ftm = player.playerStats["ftm"].getStatAdj(label)
            try:
                self.statProj[label] += round(ftm)
            except TypeError:
                pass



class TeamTpm(TeamStat):

    def __init__(self, team):
        super().__init__("tpm", team)


    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = 0
        for player in chain(self.team.starters,self.team.bench):
            tpm = player.playerStats["tpm"].getStatAdj(label)
            try:
                self.statProj[label] += round(tpm)
            except TypeError:
                pass


class TeamPts(TeamStat):

    def __init__(self, team):
        super().__init__("points", team)


    def setStat(self, formatting):
        label = formatting["label"]
        self.statProj[label] = 0
        for player in chain(self.team.starters,self.team.bench):
            pts = player.playerStats["points"].getStatAdj(label)
            try:
                self.statProj[label] += round(pts)
            except TypeError:
                pass
            
       


class TeamTpaPer(TeamStat):

    def __init__(self, team):
        super().__init__("three_per", team)

    def setStats(self):
        self.seasonProj = self.negotiateStat("totals", "season", "all")
        self.monthProj = self.negotiateStat("totals", "month", "all")
        self.homeAwayProj = self.negotiateStat("totals", "season", self.team.homeAway)        
        self.lineupProj = self.negotiateStat("lineup", "season", "all")



class TeamTpa(TeamStat):

    def __init__(self, team):
        super().__init__("tpa", team)


    def setStats(self):
        threePer = self.team.teamStats["three_per"]
        fga = self.team.teamStats["fga"]

        self.seasonProj = fga.seasonProj * threePer.seasonProj
        self.monthProj = fga.monthProj * threePer.monthProj
        self.homeAwayProj = fga.homeAwayProj * threePer.homeAwayProj
        self.lineupProj = fga.lineupProj * threePer.lineupProj

        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)

        

class TeamFtaPer(TeamStat):

    def __init__(self, team):
        super().__init__("ft_per", team)


    def setStats(self):
        self.seasonProj = self.negotiateStat("totals", "season", "all")
        self.monthProj = self.negotiateStat("totals", "month", "all")
        self.homeAwayProj = self.negotiateStat("totals", "season", self.team.homeAway)        
        self.lineupProj = self.negotiateStat("lineup", "season", "all")



class TeamFta(TeamStat):

    def __init__(self, team):
        super().__init__("fta", team)
        
        
    def setStats(self):
        ftaPer = self.team.teamStats["ft_per"]
        fouls = self.team.matchup.getOpp(self).teamStats["fouls"]

        self.seasonProj = fouls.seasonProj * ftaPer.seasonProj
        self.monthProj = fouls.monthProj * ftaPer.monthProj
        self.homeAwayProj = fouls.homeAwayProj * ftaPer.homeAwayProj
        self.lineupProj = fouls.lineupProj * ftaPer.lineupProj

        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)

        
class TeamBlkPer(TeamStat):

    def __init__(self, team):
        super().__init__("blk_per", team)


    def setStats(self):
        self.seasonProj = self.negotiateStat("totals", "season", "all")
        self.monthProj = self.negotiateStat("totals", "month", "all")
        self.homeAwayProj = self.negotiateStat("totals", "season", self.team.homeAway)        
        self.lineupProj = self.negotiateStat("lineup", "season", "all")


        
class TeamBlk(TeamStat):

    def __init__(self, team):
        super().__init__("blk", team)


    def setStats(self):
        blkPer = self.team.teamStats["blk_per"]
        fga = self.team.matchup.getOpp(self).teamStats["fga"]

        self.seasonProj = fga.seasonProj * blkPer.seasonProj
        self.monthProj = fga.monthProj * blkPer.monthProj
        self.homeAwayProj = fga.homeAwayProj * blkPer.homeAwayProj
        self.lineupProj = fga.lineupProj * blkPer.lineupProj

        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)


class TeamORebPer(TeamStat):

    def __init__(self, team):
        super().__init__("oreb_per", team)


    def setStats(self):
        self.seasonProj = self.negotiateStat("totals", "season", "all")
        self.monthProj = self.negotiateStat("totals", "month", "all")
        self.homeAwayProj = self.negotiateStat("totals", "season", self.team.homeAway)        
        self.lineupProj = self.negotiateStat("lineup", "season", "all")


        
class TeamOReb(TeamStat):

    def __init__(self, team):
        super().__init__("oreb", team)


    def setStats(self):
        orebPer = self.team.teamStats["oreb_per"]
        fga = self.team.matchup.getOpp(self).teamStats["fga"]
        fgm = self.team.matchup.getOpp(self).teamStats["fgm"]


        self.seasonProj = (fga.seasonProj -fgm.seasonProj)* orebPer.seasonProj
        self.monthProj = (fga.monthProj -fgm.monthProj)* orebPer.monthProj
        self.homeAwayProj = (fga.homeAwayProj -fgm.homeAwayProj)* orebPer.homeAwayProj
        self.lineupProj = (fga.lineupProj -fgm.lineupProj)* orebPer.lineupProj
        
        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)



class TeamDRebPer(TeamStat):

    def __init__(self, team):
        super().__init__("dreb_per", team)


    def setStats(self):
        self.seasonProj = self.negotiateStat("totals", "season", "all")
        self.monthProj = self.negotiateStat("totals", "month", "all")
        self.homeAwayProj = self.negotiateStat("totals", "season", self.team.homeAway)        
        self.lineupProj = self.negotiateStat("lineup", "season", "all")


        
class TeamDReb(TeamStat):

    def __init__(self, team):
        super().__init__("dreb", team)


    def setStats(self):
        orebPer = self.team.teamStats["dreb_per"]
        fga = self.team.teamStats["fga"]
        fgm = self.team.teamStats["fgm"]

        self.seasonProj = (fga.seasonProj -fgm.seasonProj)* orebPer.seasonProj
        self.monthProj = (fga.monthProj -fgm.monthProj)* orebPer.monthProj
        self.homeAwayProj = (fga.homeAwayProj -fgm.homeAwayProj)* orebPer.homeAwayProj
        self.lineupProj = (fga.lineupProj -fgm.lineupProj)* orebPer.lineupProj
        
        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)



class TeamAstPer(TeamStat):

    def __init__(self, team):
        super().__init__("ast_per", team)


    def setStats(self):
        self.seasonProj = self.negotiateStat("totals", "season", "all")
        self.monthProj = self.negotiateStat("totals", "month", "all")
        self.homeAwayProj = self.negotiateStat("totals", "season", self.team.homeAway)        
        self.lineupProj = self.negotiateStat("lineup", "season", "all")


        
class TeamAst(TeamStat):

    def __init__(self, team):
        super().__init__("ast", team)


    def setStats(self):
        astPer = self.team.teamStats["ast_per"]
        fgm = self.team.teamStats["fgm"]

        self.seasonProj = fgm.seasonProj * astPer.seasonProj
        self.monthProj = fgm.monthProj * astPer.monthProj
        self.homeAwayProj = fgm.homeAwayProj * astPer.homeAwayProj
        self.lineupProj = fgm.lineupProj * astPer.lineupProj
        
        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)

        

        
class TeamFTurn(TeamStat):

    def __init__(self, team):
        super().__init__("forced_turn", team)


class TeamStl(TeamStat):

    def __init__(self, team):
        super().__init__("stl", team)


    def setStats(self):
        fTurn = self.team.teamStats["forced_turn"]
        turn = self.team.matchup.getOpp(self).teamStats["turn"]

        self.seasonProj = turn.seasonProj - fTurn.seasonProj
        self.monthProj = turn.monthProj - fTurn.monthProj
        self.homeAwayProj = turn.homeAwayProj - fTurn.homeAwayProj
        self.lineupProj = turn.lineupProj - fTurn.lineupProj

        self.seasonProj = round(self.seasonProj)
        self.monthProj = round(self.monthProj)
        self.homeAwayProj = round(self.homeAwayProj)
        self.lineupProj = round(self.lineupProj)


##    def setStats(self):
##        uturn = self.team.matchup.getOpp(self).teamStats["unforce_turn"]
##        turn = self.team.matchup.getOpp(self).teamStats["turn"]
##
##        self.seasonProj = turn.seasonProj - uturn.seasonProj
##        self.monthProj = turn.monthProj - uturn.monthProj
##        self.homeAwayProj = turn.homeAwayProj - uturn.homeAwayProj
##        self.lineupProj = turn.lineupProj - uturn.lineupProj

