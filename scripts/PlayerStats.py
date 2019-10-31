bucketCmd = ("SELECT num, bucket, stat_avg, stat_15, stat_85, stat_40, stat_60, stat_max, stat_min FROM item_totals AS totals WHERE proj_id = '{0[projId]} AND item_type = '{0[item]}' AND item_id = {0[itemId]} AND stat_id = '{0[statId]}' AND time_frame = '{0[timeFrame]}' AND home_away = '{0[homeAway]}")


class Projection:

    def __init__(self, label):

        items = label.split("-")
        self.label = label
        self.title = items[0]
        self.timeFrame = items[1]
        self.homeAway = items[2]


    def projEst(self, player, statId):
        formatting = {"item": "player",
                      "item_id": player.getId(),
                      "stat_id": statId,
                      "timeFrame": self.timeFrame,
                      "homeAway": self.homeAway}
        
        db.curs.execute(bucketCmd.format(formatting))


    def getFormatting(self, player, formatType):
        
                      
        
##        playerFormat = {"starter": self.player.starter, "item": "player", "itemId": self.player.playerId, "table": "player_{}".format(table), "season":timeFrame, "statId":self.statId, "home": homeAway, "offDef":"off"}
##        vsPlayerFormat = {"starter": self.player.starter, "item": "player", "itemId": self.player.playerId, "table":"player_{}".format(table), "season":timeFrame, "statId":self.statId, "home": homeAway, "offDef":"def"}
##        oppDFormat = {"starter": self.player.starter, "item": "team", "itemId": self.player.team.oppId, "table":"{}_vs_pos".format(table if table == "lineup" else "team"), "season":timeFrame, "statId":self.statId, "home": oppHomeAway, "offDef":"def"}
##        vsOppDFormat = {"starter": self.player.starter, "item": "team", "itemId": self.player.team.oppId, "table":"{}_vs_pos".format(table if table == "lineup" else "team"), "season":timeFrame, "statId":self.statId, "home": oppHomeAway, "offDef":"off"}
##        matchFormat = {"match":True, "item": "player", "itemId": self.player.playerId, "table":"matchup_player", "season":"season", "statId":self.statId, "home": "all", "offDef":"off"}
        




class PlayerStat:

    def __init__(self, statId, player):

        self.statId = statId
        self.player = player
        self.projTypes = self.player.getProjTypes()
        self.teamStat = player.team.teamStats.get(statId, None)
            
        self.statEst = {}
        self.statAdj = {}


    def getJson(self):
        jsonDict = {"statId":self.statId,
                    "statEst":self.statEst,
                    "statProj":self.statProj}        
        return jsonDict

    
    def setStatEst(self):
        minutes = self.player.playerStats["mins"]

        for projType in self.projTypes:
            try:
                label = projType.label
                self.statEst[label] = round(self.negotiateStat(projType)) * (minutes.statProj[label]/48)
                self.teamStat.addToTotal(label, self.statEst[label])
            except TypeError:
                self.statEst[label] = 0


    def setStats(self):
        for projType in self.projTypes:
            label = projType.label
            self.statAdj[label] = round(teamStat[label] * (self.statEst[label]/self.teamStat.getTotal(label)))

                       
    def negotiateStat(self, projType):
        totals = []
        oppX = 1
        playerX = 1
        index = 2
        result = 0
     
        playerResult = db.curs.execute(playerBucketCmd.format(formatting)).fetchone()
        vsPlayerResult = db.curs.execute(playerBucketCmd.format(formatting)).fetchone()
        if playerResult[0] > 0:
            try:
                playerX = playerResult[2]/vsPlayerResult[2]
            except ZeroDivisionError:
                pass
            
        oppDResult =  db.curs.execute(playerBucketCmd.format(formatting)).fetchone()
        vsOppDResult = db.curs.execute(playerBucketCmd.format(formatting)).fetchone()
        if oppDResult[0] > 0:
            try:
                oppX = oppDResult[2]/vsOppDResult[2]
            except ZeroDivisionError:
                pass

        matchResults = db.curs.execute(matchBucketCmd.format(formatting)).fetchone()
        
        simResults = self.setSimFormat(formatting, playerResult, oppDResult)
        if simResults:
            index = {"poor":3,"ok":5,"average":2,"good":6, "elite":4}.get(simResults[1], 2)
            totals.append(simResults[index])

        if playerResult[0] > 0:
            totals.append(playerResult[index]*oppX)

        if oppDResult[0] > 0:
            totals.append(oppDResult[index]*playerX)

        if matchResults and matchResults[0] > 0:
            totals.append(matchResults[index])

        #pprint(totals)

        if len(totals):
            result = numpy.mean(totals)
        return xyz
            
        #pprint(playerResult)
        #pprint(oppDResult)
        #pprint(matchResults)




        
##        print("Team Result", teamResult)
##        print("Team Vs", teamResultVs)
##        print("Opp", oppDResult)
##        print("Opp Vs", oppDResultVs)

        






##        results = db.curs.execute(cmd.format(simResultFormat)).fetchall()
##        
##        
##
##        oppCmd = "SELECT team_id FROM {0[table1]}_vs_pos WHERE starter = {0[starter]} AND off_def = 'off' AND stat_id = '{0[stat]}' AND time_frame = '{0[timeFrame]}' AND home_away = '{0[homeAway]}' AND pos = '{0[pos]}' AND bucket = '{0[dBucket]}'"
##        playerCmd = "SELECT player_id FROM player_{0[table2]} WHERE starter = {0[starter]} AND off_def = 'off' AND stat_id = '{0[stat]}' AND time_frame = '{0[timeFrame]}' AND home_away = '{0[homeAway]}' AND bucket = '{0[oBucket]}'"
##        simGames = "SELECT stats.game_id, stats.player_id FROM player_stats AS stats INNER JOIN positions ON stats.game_id = positions.game_id AND stats.player_id = positions.player_id INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id WHERE stats.player_id IN ("+playerCmd+") AND stats.opp_id IN ("+oppCmd+") AND positions.position = '{0[pos]}' AND stats.starter = {0[starter]}"
##        cmd = "SELECT gd.minutes, " + ", ".join(["stats.{0}".format(s) for s in gameStats["player"]]) + " FROM player_stats AS stats INNER JOIN ( {0[gdCmd]} ) AS gd ON stats.game_id = gd.game_id INNER JOIN ("+simGames+") AS sim ON stats.game_id = sim.game_id AND stats.player_id = sim.player_id"
##        #print(cmd.format(simResultFormat))
##
##        newList = []
##        for result in results:
##            try:
##                newList.append(func.get(self.statId, lambda result, item, i: r(self.statId, result, item, i))(result, "player", 0)/result[0]*48)
##            except ZeroDivisionError:
##                pass
##        simResults = tableFormat(self.statId, newList, simResultFormat)
##
##        simResults = [simResults[item] for item in ("num", "bucket", "stat_avg", "stat_15", "stat_85", "stat_40", "stat_60", "stat_max", "stat_min")]
##        #pprint(simResults)
        

    


class PlayerPct(PlayerStat):

    def __init__(self, statId, player):
        super().__init__(statId, player)


    def calcStat(self, table, timeFrame, homeAway):

        totals = []
        index = 2

        if homeAway == "all":
            oppHomeAway = homeAway
        else:
            oppHomeAway = "away" if homeAway == "home" else "away"
            
        playerFormat = {"starter": self.player.starter, "item": "player", "itemId": self.player.playerId, "table": "player_{}".format(table), "season":timeFrame, "statId":self.statId, "home": homeAway, "offDef":"off"}
        oppDFormat = {"starter": self.player.starter, "item": "team", "itemId": self.player.team.oppId, "table":"{}_vs_pos".format(table if table == "lineup" else "team"), "season":timeFrame, "statId":self.statId, "home": oppHomeAway, "offDef":"def"}
        matchFormat = {"match":True, "item": "player", "itemId": self.player.playerId, "table":"matchup_player", "season":"season", "statId":self.statId, "home": "all", "offDef":"off"}
     
        playerResult = db.curs.execute(playerBucketCmd.format(playerFormat)).fetchone()
        oppDResult =  db.curs.execute(playerBucketCmd.format(oppDFormat)).fetchone()
        
        #pprint(playerResult)
        #pprint(oppDResult)
        
        matchResults = db.curs.execute(matchBucketCmd.format(matchFormat)).fetchone()
        #pprint(matchResults)
##        print("Team Result", teamResult)
##        print("Team Vs", teamResultVs)
##        print("Opp", oppDResult)
##        print("Opp Vs", oppDResultVs)
        simResultFormat = {"player_id":-1,"homeAway": homeAway, "pos": self.player.pos, "starter": self.player.starter, "table1":table if table == "lineup" else "team", "table2": table, "item":"player", "gdCmd":monthCmd if timeFrame == "month" else seasonCmd, "timeFrame":timeFrame, "stat":self.statId, "oBucket": playerResult[1], "dBucket":oppDResult[1]}   

        oppCmd = "SELECT team_id FROM {0[table1]}_vs_pos WHERE starter = {0[starter]} AND off_def = 'off' AND stat_id = '{0[stat]}' AND time_frame = '{0[timeFrame]}' AND home_away = '{0[homeAway]}' AND pos = '{0[pos]}' AND bucket = '{0[dBucket]}'"
        playerCmd = "SELECT player_id FROM player_{0[table2]} WHERE starter = {0[starter]} AND off_def = 'off' AND stat_id = '{0[stat]}' AND time_frame = '{0[timeFrame]}' AND home_away = '{0[homeAway]}' AND bucket = '{0[oBucket]}'"
        simGames = "SELECT stats.game_id, stats.player_id FROM player_stats AS stats INNER JOIN positions ON stats.game_id = positions.game_id AND stats.player_id = positions.player_id INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id WHERE stats.player_id IN ("+playerCmd+") AND stats.opp_id IN ("+oppCmd+") AND positions.position = '{0[pos]}' AND stats.starter = {0[starter]}"
        cmd = "SELECT gd.minutes, " + ", ".join(["stats.{0}".format(s) for s in gameStats["player"]]) + " FROM player_stats AS stats INNER JOIN ( {0[gdCmd]} ) AS gd ON stats.game_id = gd.game_id INNER JOIN ("+simGames+") AS sim ON stats.game_id = sim.game_id AND stats.player_id = sim.player_id"
        #print(cmd.format(simResultFormat))
        results = db.curs.execute(cmd.format(simResultFormat)).fetchall()
        newList = []
        for result in results:
            try:
                newList.append(func.get(self.statId, lambda result, item, i: r(self.statId, result, item, i))(result, "player", 0)/result[0]*48)
            except ZeroDivisionError:
                pass
        simResults = tableFormat(self.statId, newList, simResultFormat)

        simResults = [simResults[item] for item in ("num", "bucket", "stat_avg", "stat_15", "stat_85", "stat_40", "stat_60", "stat_max", "stat_min")]
        #pprint(simResults)
        if simResults[0] > 0:
            index = {"poor":3,"ok":5,"average":2,"good":6, "elite":4}.get(simResults[1], 2)
            totals.append(simResults[index])

        if playerResult[0] > 0:
            totals.append(playerResult[index])

        if oppDResult[0] > 0:
            totals.append(oppDResult[index])

        if matchResults and matchResults[0] > 0:
            totals.append(matchResults[index])

        #pprint(totals)

        if not len(totals):
            xyz = 0

        else:
            xyz = numpy.mean(totals)
        return xyz


    def setStats(self):
        for projType in self.projTypes:
            try:
                self.statAdj[projType] = self.calcStat(projType)
            except TypeError:
                self.statAdj[projType] = 0


    






class PlayerMins(PlayerStat):
        
    def __init__(self, player):
        super().__init__("mins", player)


    def setStatEst(self):
         for projType in self.projTypes:
            try:
                self.statEst[projType] = round(self.negotiateStat(projType))
            except TypeError:
                self.statEst[projType] = 0


class PlayerFouls(PlayerStat):
        
    def __init__(self, player):
        super().__init__("fouls", player)

        
class PlayerTurn(PlayerStat):

    
        
    def __init__(self, player):
        super().__init__("turn", player)

    
class PlayerFgPct(PlayerPct):
        
    def __init__(self, player):
        super().__init__("fg_pct", player)
        

    


class PlayerFtPct(PlayerPct):
        
    def __init__(self, player):
        super().__init__("ft_pct", player)
        

class PlayerTpPct(PlayerPct):
        
    def __init__(self, player):
        super().__init__("tp_pct", player)


class PlayerThreePer(PlayerStat):
        
    def __init__(self, player):
        super().__init__("three_per", player)


    def setStats(self):
         for projType in self.projTypes:
            self.statAdj[projType] = self.statEst[projType]
        

class PlayerFgm(PlayerStat):

    def __init__(self, player):
        super().__init__("fgm", player)


    def setStats(self):

        fgPct = self.player.playerStats["fg_pct"]
        fga = self.player.playerStats["fga"]
        
        for projType in self.projTypes:
            try:
                self.statAdjt[projType] = round(fga.statAdj[projType]*fgPct.statAdj[projType])
            except TypeError:
                self.statAdj[projType] = 0
                   

class PlayerFga(PlayerStat):
 
    def __init__(self, player):
        super().__init__("fga", player)

   
class PlayerFta(PlayerStat):
        
    def __init__(self, player):
        super().__init__("fta", player)


class PlayerFtm(PlayerStat):
        
    def __init__(self, player):
        super().__init__("ftm", player)


    def setStats(self):
        ftPct = self.player.playerStats["ft_pct"]
        fta = self.player.playerStats["fta"]
        
        for projType in self.projTypes:
            try:
                self.statAdj[projType] = round(fta.statAdj[projType]*ftPct.statAdj[projType])
            except TypeError:
                self.statAdj[projType] = 0
            

class PlayerTpa(PlayerStat):
        
    def __init__(self, player):
        super().__init__("tpa", player)


    def setStatEst(self):
        teamStat = self.player.team.teamStats[self.statId]
        fga = self.player.playerStats["fga"]
        threePer = self.player.playerStats["three_per"]

        for projType in self.projTypes:
            try:
                self.statEst[projType] = fga.statEst[projType]*threePer.statEst[projType]
                teamStat.addToTotal(projType, self.statEst[projType])
            except TypeError:
                self.statEst[projType] = 0


    def setStats(self):
        for projType in self.projTypes:
            self.statAdj[projType] = round(self.statEst[projType])


class PlayerTpm(PlayerStat):
        
    def __init__(self, player):
        super().__init__("tpm", player)
        

    def setStats(self):
        tpPct = self.player.playerStats["tp_pct"]
        tpa = self.player.playerStats["tpa"]

        for projType in self.projTypes:
            try:
                self.statAdj[projType] = round(tpa.statProj[projType]*tpPct.statProj[projType])
            except TypeError:
                self.statAdj[projType] = 0


class PlayerDReb(PlayerStat):
        
    def __init__(self, player):
        super().__init__("dreb", player)


class PlayerOReb(PlayerStat):
        
    def __init__(self, player):
        super().__init__("oreb", player)


class PlayerStl(PlayerStat):
        
    def __init__(self, player):
        super().__init__("stl", player)


class PlayerAst(PlayerStat):
        
    def __init__(self, player):
        super().__init__("ast", player)


class PlayerBlk(PlayerStat):
        
    def __init__(self, player):
        super().__init__("blk", player)


class PlayerPts(PlayerStat):

        
    def __init__(self, player):
        super().__init__("points", player)


    def setStats(self):
        fgm = self.player.playerStats["fgm"]
        ftm = self.player.playerStats["ftm"]
        tpm = self.player.playerStats["tpm"]
        for projType in self.projTypes:
            try:
                self.statEst[projType] = round(fgm.statAdj[projType]*2 + ftm.statAdj[projType] + tpm.statAdj[projType])
            except TypeError:
                self.statAdj[projType] = 0
