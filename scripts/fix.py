class Projection:

    def __init__(self, formatting):

        self.formatting = formatting


    def getFormatLists(self, itemId):
        raise AssertionError


    def makeBuckets(self, formatting):
        raise AssertionError


    def bucketDrop(self, formatting):
        raise AssertionError


    def inputResults(self, formatting):
        raise AssertionError


class TeamProjection(Projection):

    def __init__(self, formatting):
        super().__init__(formatting)


    def getFormatLists(self, itemId):
        formatList = []
        for timeFrame, gdCmd in (("season",seasonCmd), ("month", monthCmd), ("twoWeeks", twoWeeksCmd)):
            for homeAway, haCmd in (("home", homeCmd), ("away", awayCmd), ("all", allCmd)):

                for i, d in enumerate(self.formatting["Ds"]):
                    newFormat = self.formatting.copy()
                    newFormat["proj_id"] = self.formatting["proj_id"]+d
                    newFormat
                    for key, value in (("item_id",itemId),
                                       ("proj_id",self.formatting["proj_id"]+d),
                                       ("check_id", self.formatting["check_id"]+d),
                                       ("time_frame",timeFrame),
                                       ("home_away",homeAway),
                                       ("i",i),
                                       ("gdCmd",gdCmd),
                                       ("haCmd", haCmd),
                                       ("whereCmd", " WHERE stats.team_id = ?")):
                        newFormat[key] = value
                    formatList.append(newFormat)
        return formatList


    def makeBuckets(self, formatting):
        for stat in teamCompute:
            formatting["stat_id"] = stat
            #pprint(formatting)

            results = [x[0] for x in db.curs.execute(avgCmd.format(formatting)).fetchall()]
            #pprint(results)

            formatting = calcItemList(stat, results, formatting)
            formatting["item_id"] = "all"
            db.insert(itemTotalsTable, formatting)



    def bucketDrop(self, formatting):
        try:
            formatting = setBucket(formatting)
            db.curs.execute(updateBucketCmd.format(formatting))
        except TypeError:
            pass
        

    def inputResults(self, formatting):
        results = db.curs.execute(baseTeamCmd.format(formatting),(formatting["item_id"],)).fetchall()
        statList = dict(zip([x for x in teamCompute], [[] for i in range(len(teamCompute))]))
        for result in results:
            #print(result)
            for stat in teamCompute:
                try:
                    statList[stat].append(func.get(stat, lambda result, item, i: r(stat, result, item, i))(result, formatting["item_type"], formatting["i"])/result[0]*48)
                    #pprint(statList)
                except ZeroDivisionError:
                    pass

            for stat in teamCompute:
                formatting = calcItemList(stat, statList[stat], formatting)
                if formatting["num"]:
                    try:
                        db.insert(itemTotalsTable, formatting)
                    except sqlite3.IntegrityError:
                        pass
                        
        db.conn.commit()

                    
  
class PlayerProjection(Projection):

    def __init__(self, formatting):
        super().__init__(formatting)


    def getFormatLists(self, itemId):
        formatList = []
        for timeFrame, gdCmd in (("season",seasonCmd), ("month", monthCmd), ("twoWeeks", twoWeeksCmd)):
            for homeAway, haCmd in (("home", homeCmd), ("away", awayCmd), ("all", allCmd)):
                newFormat = self.formatting.copy()
                playerPos = [x[0] for x in db.curs.execute(playerPosCmd.format(newFormat), (itemId,)).fetchall()]
                playerPos.append(None)
                for pos in set(playerPos):
                    posCmd = " INNER JOIN positions AS pos ON stats.game_id = pos.game_id AND stats.player_id = pos.player_id" if pos else ""
                    for starter, whereCmd in ((None," WHERE stats.player_id = ?"), (1, " WHERE player_id = ?"+starterCmd), (0, " WHERE player_id = ?"+benchCmd)):
                        projId = ""
                        if pos:
                            if pos == "G":
                                pos = "PG"
                            if pos == "F":
                                pos = "SF"
                            projId += "_{}".format(pos)
                        if starter in (1,0):
                            projId += "_{}".format(pos)
                       
                for key, value in (("item_id",itemId),
                                   ("proj_id",self.formatting["proj_id"]),
                                   ("check_id", self.formatting["check_id"]),
                                   ("time_frame",timeFrame),
                                   ("home_away",homeAway),
                                   ("i",0),
                                   ("gdCmd",gdCmd),
                                   ("haCmd", haCmd),
                                   ("posCmd", posCmd),
                                   ("whereCmd", whereCmd)):
                    newFormat[key] = value
                    formatList.append(newFormat)
        return formatList


    def makeBuckets(self, formatting):
        for stat in teamCompute:
            formatting["stat_id"] = stat
            #pprint(formatting)

            results = [x[0] for x in db.curs.execute(avgCmd.format(formatting)).fetchall()]
            #pprint(results)

            formatting = calcItemList(stat, results, formatting)
            formatting["item_id"] = "all"
            db.insert(itemTotalsTable, formatting)



    def bucketDrop(self, formatting):
        try:
            formatting = setBucket(formatting)
            db.curs.execute(updateBucketCmd.format(formatting))
        except TypeError:
            pass
        

    def inputResults(self, formatting):
        results = db.curs.execute(baseTeamCmd.format(formatting),(formatting["item_id"],)).fetchall()
        statList = dict(zip([x for x in teamCompute], [[] for i in range(len(teamCompute))]))
        for result in results:
            #print(result)
            for stat in teamCompute:
                try:
                    statList[stat].append(func.get(stat, lambda result, item, i: r(stat, result, item, i))(result, formatting["item_type"], formatting["i"])/result[0]*48)
                    #pprint(statList)
                except ZeroDivisionError:
                    pass

            for stat in teamCompute:
                formatting = calcItemList(stat, statList[stat], formatting)
                if formatting["num"]:
                    try:
                        db.insert(itemTotalsTable, formatting)
                    except sqlite3.IntegrityError:
                        pass
                        
        db.conn.commit()


        




                    

                   

                                    
                     

        
        

