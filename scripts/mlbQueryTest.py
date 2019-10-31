import sqlite3
from matplotlib import pyplot as plt
from pprint import pprint
from operator import itemgetter
from itertools import groupby
from json import dump

filePath = "/home/ededub/FEFelson/MLB/"

conn = sqlite3.connect("/home/ededub/FEFelson/MLB.db")
curs = conn.cursor()



ipNum = 30
##pitchers = []
##
##cmd = "SELECT DISTINCT pitchingStats.playerId FROM pitchingStats"
##curs.execute(cmd)
##players = [x[0] for x in curs.fetchall()]
##
##for playerId in players:
##    try:
##        cmd = "SELECT firstName, lastName FROM players WHERE playerId = {}"
##        curs.execute(cmd.format(playerId))
##        firstName, lastName = curs.fetchone()
##
##        print(firstName, lastName)        
##        player = {"firstName": firstName, "lastName": lastName, "playerId": playerId}
##
##        for year in (2015,2016,2017):
##            cmd = "SELECT ((SUM(er) * {0})/ SUM(ip)), ((SUM(bb) * {0})/ SUM(ip)), ((SUM(h) * {0})/ SUM(ip)), ((SUM(k) * {0})/ SUM(ip)) FROM pitchingStats, games WHERE pitchingStats.gameId = games.gameId AND games.season = {1}"
##            curs.execute(cmd.format(ipNum, year))
##            erNum, bbNum, hNum, kNum = curs.fetchone()
##
##            cmd = "SELECT SUM(w), SUM(sv), SUM(k), (SUM(ip) *1.0 / 24.0), (SUM(er)*1.0 / 24.0), (SUM(bb) / 24.0), (SUM(h) / 24.0), (SUM(k) / 24.0) FROM pitchingStats, games WHERE pitchingStats.playerId = {} AND games.gameId = pitchingStats.gameId AND games.season = {} GROUP BY pitchingStats.playerId HAVING SUM(er) > 0"
##            curs.execute(cmd.format(playerId, year))
##            w, sv, k, newIP, newER, newBB, newH, newK = curs.fetchone()
##            stats = {"score": 0}
##            statConvert = {"w": w, "sv": sv, "k":k}
##            
##            totalIP = ipNum + newIP
##            totalER = erNum + newER
##            totalBB = bbNum + newBB
##            totalH = hNum + newH
##            totalK = kNum + newK
##
##            for stat in ("w", "sv", "er", "k", "era", "whip", "k9"):
##                maxNum = None
##                with open(filePath+stat) as fileIn:
##                    for line in fileIn:
##                        lineYear, num = line.split()
##                        if int(lineYear) == year:
##                            maxNum = num
##
##                if stat == "er":
##                    stats[stat] = 10 * float(maxNum) / newER
##
##                elif stat == "era":
##                    oldERA = (erNum * 9)/ ipNum
##                    newERA = ((totalER *9)/totalIP) 
##                    num = oldERA - newERA 
##                    stats[stat] = 10 * num / float(maxNum)
##
##                elif stat == "whip":
##                    oldWHIP = (bbNum + hNum) /ipNum
##                    newWHIP = (totalBB + totalH) / totalIP 
##                    num = oldWHIP - newWHIP
##                    stats[stat] = 10 * num / float(maxNum)
##
##                elif stat == "k9":
##                    oldK9 = (kNum * 9)/ ipNum
##                    newK9 = (totalK *9)/ totalIP 
##                    num = newK9 - oldK9
##                    stats[stat] = 10 * num / float(maxNum)
##
##                else:
##                    stats[stat] = 10 * statConvert[stat] / float(maxNum)
##
##                stats["score"] = stats["score"] + stats[stat]
##            player[year] = stats
##        pitchers.append(player)
##    except TypeError:
##        pass
##    except ValueError:
##        print("ValueError")
##
##for player in pitchers:
##    pprint(player)
##
##    print("\n\n\n")  
##        
##with open("/home/ededub/FEFelson/MLB/pitchers.json", "w") as fileOut:
##    dump({"pitchers":pitchers}, fileOut)



##
##fileOut = open(filePath+"k9", "w")
##maxNum = []
##for year in (2015,2016,2017):
##    cmd = "SELECT ((SUM(er) * {0})/ SUM(ip)), ((SUM(bb) * {0})/ SUM(ip)), ((SUM(h) * {0})/ SUM(ip)), ((SUM(k) * {0})/ SUM(ip)) FROM pitchingStats, games WHERE pitchingStats.gameId = games.gameId AND games.season = {1}"
##    curs.execute(cmd.format(ipNum, year))
##    erNum, bbNum, hNum, kNum = curs.fetchone()
##
####    print( (erNum * 9)/ ipNum)
####    print((bbNum + hNum) / ipNum)
####    print( (kNum * 9)/ ipNum)
##
##    cmd = "SELECT (SUM(ip) *1.0 / 24.0), (SUM(er)*1.0 / 24.0), (SUM(bb) / 24.0), (SUM(h) / 24.0), (SUM(k) / 24.0) FROM pitchingStats, games WHERE games.gameId = pitchingStats.gameId AND games.season = {} GROUP BY pitchingStats.playerId HAVING SUM(er) > 0"
##    curs.execute(cmd.format(year))
##    for player in curs.fetchall():
##        newIP, newER, newBB, newH, newK = player
####        print(newIP, newER, newBB, newH, newK)
##
##        totalIP = ipNum + newIP
##        totalER = erNum + newER
##        totalBB = bbNum + newBB
##        totalH = hNum + newH
##        totalK = kNum + newK
##
##        
##
##        oldERA = (erNum * 9)/ ipNum
##        oldWHIP = (bbNum + hNum) /ipNum
##        oldK9 = (kNum * 9)/ ipNum
##
##        
##
##        newERA = (totalER * 9)/ totalIP
##        newWHIP = (totalBB + totalH) / totalIP
##        newK9 = (totalK *9)/ totalIP
##        
##
##        maxNum.append(newK9 - oldK9)
##
##    print(max(maxNum))
##
##
##    fileOut.write("{} {}\n".format(year, max(maxNum)))
##fileOut.close()
##

##batters = []
##
##cmd = "SELECT DISTINCT battingStats.playerId FROM battingStats WHERE playerId NOT IN ( SELECT DISTINCT playerId FROM pitchingStats)"
##curs.execute(cmd)
##players = [x[0] for x in curs.fetchall()]
##
##for playerId in players:
##    try:
##        cmd = "SELECT firstName, lastName FROM players WHERE playerId = {}"
##        curs.execute(cmd.format(playerId))
##        firstName, lastName = curs.fetchone()
##
##        print(firstName, lastName)
##
##        
##        player = {"firstName": firstName, "lastName": lastName, "playerId": playerId}
##
##        
##        for year in (2015,2016,2017):
##            cmd = "SELECT ((SUM(bb) * {0})/ SUM(ab)), ((SUM(h) * {0})/ SUM(ab)), ((SUM(dbl) * {0})/ SUM(ab)), ((SUM(tpl) * {0})/ SUM(ab)), ((SUM(hr) * {0})/ SUM(ab)), ((SUM(sf) * {0})/ SUM(ab)), ((SUM(s) * {0})/ SUM(ab)) from battingStats, games WHERE games.gameId = battingStats.gameId AND games.season = {1} AND battingStats.playerId NOT IN ( SELECT DISTINCT pitchingStats.playerId FROM pitchingStats)"
##            curs.execute(cmd.format(abNum, year))
##            bbNum, hNum, dblNum, tplNum, hrNum, sfNum, sNum = curs.fetchone()
##
##                        
##            cmd = "SELECT SUM(ab), SUM(bb), SUM(r), SUM(h), SUM(dbl), SUM(tpl), SUM(hr), SUM(rbi), SUM(sb), SUM(sf), SUM(s) FROM battingStats, players, games WHERE battingStats.playerId = players.playerId AND battingStats.playerId = {} AND battingStats.gameId = games.gameId AND games.season = {} GROUP BY battingStats.playerId"
##            curs.execute(cmd.format(playerId,year))
##        
##            ab, bb, r, h, dbl, tpl, hr, rbi, sb, sf, s = curs.fetchone()
##            stats = {"score": 0}
##            statConvert = {"r":r, "h":h, "hr":hr, "rbi":rbi, "sb":sb}
##
##            totalAB = abNum + (ab/24.0)
##            totalBB = bbNum + (bb/24.0)
##            totalH = hNum + (h/24.0)
##            totalDBL = dblNum + (dbl/24.0)
##            totalTPL = tplNum + (tpl/24.0)
##            totalHR = hrNum + (hr/24.0)
##            totalSF = sfNum + (sf/24.0)
##            totalS = sNum + (s/24.0)
##                       
##            for stat in ("r", "h", "hr", "rbi", "sb", "tb", "avg", "ops"):
##                maxNum = None
##                with open(filePath+stat) as fileIn:
##                    for line in fileIn:
##                        lineYear, num = line.split()
##                        if int(lineYear) == year:
##                            maxNum = num
##
##                if stat == "avg":
##                    num = (totalH/totalAB) - (hNum/abNum)
##                    stats[stat] = 10 * num / float(maxNum)
##
##                elif stat == "ops":
##                    oldSLG = (hNum+dblNum+(tplNum*2)+(hrNum*3))/190
##                    oldOBP = (hNum+bbNum)/(abNum+bbNum+sfNum+sNum)
##
##                    newSLG = (totalH+totalDBL+(totalTPL*2)+(totalHR*3))/totalAB
##                    newOBP = (totalH+totalBB)/(totalAB+totalBB+totalSF+totalS)
##
##                    num = (newSLG+newOBP) - (oldSLG+oldOBP)
##                    stats[stat] = 10 * num/float(maxNum)
##                    
##                elif stat == "tb":
##                    stats[stat] = 10 * float(h+dbl+tpl*2+hr*3) / float(maxNum)
##                else:
##                    stats[stat] = 10 * statConvert[stat] / float(maxNum)
##
##                stats["score"] = stats["score"] + stats[stat]
##            player[year] = stats
##        batters.append(player)
##    except TypeError:
##            pass
##
##for player in batters:
##    pprint(player)
##
##    print("\n\n\n")  
##        
##with open("/home/ededub/FEFelson/MLB/batters.json", "w") as fileOut:
##    dump({"batters":batters}, fileOut)




        
    
##    fileOut.write("{} {}\n".format(year, maxStat)) 
            

##
##abNum = 190
##
####for year in (2015, 2016, 2017):
####    
####    cmd = "SELECT ((SUM(bb) * {0})/ SUM(ab)), ((SUM(h) * {0})/ SUM(ab)), ((SUM(dbl) * {0})/ SUM(ab)), ((SUM(tpl) * {0})/ SUM(ab)), ((SUM(hr) * {0})/ SUM(ab)), ((SUM(sf) * {0})/ SUM(ab)), ((SUM(s) * {0})/ SUM(ab)) from battingStats, games WHERE games.gameId = battingStats.gameId AND games.season = {1} AND battingStats.playerId NOT IN ( SELECT DISTINCT pitchingStats.playerId FROM pitchingStats)"
####    curs.execute(cmd.format(abNum, year))
####    bbNum, hNum, dblNum, tplNum, hrNum, sfNum, sNum = curs.fetchone()
####
####    
####    maxOPS = []
####    maxAVG = []
####
####
####    cmd = "SELECT (SUM(ab) / 24.0), (SUM(bb) / 24.0), (SUM(h) / 24.0), (SUM(dbl) / 24.0), (SUM(tpl) / 24.0), (SUM(hr) / 24.0), (SUM(sf) / 24.0), (SUM(s) / 24.0) from battingStats, games WHERE games.gameId = battingStats.gameId AND games.season = {} AND battingStats.playerId NOT IN ( SELECT DISTINCT pitchingStats.playerId FROM pitchingStats) GROUP BY battingStats.playerId"
####    curs.execute(cmd.format(year))
####    for player in curs.fetchall():
####        newAB, newBB, newH, newDBL, newTPL, newHR, newSF, newS = player
####
####
####        totalAB = abNum + newAB
####        totalBB = bbNum + newBB
####        totalH = hNum + newH
####        totalDBL = dblNum + newDBL
####        totalTPL = tplNum + newTPL
####        totalHR = hrNum + newHR
####        totalSF = sfNum + newSF
####        totalS = sNum + newS
####
####        oldAVG = hNum/abNum
####        newAVG = totalH/ totalAB
####
####        oldSLG = (hNum+dblNum+(tplNum*2)+(hrNum*3))/190
####        oldOBP = (hNum+bbNum)/(abNum+bbNum+sfNum+sNum)
####
####        newSLG = (totalH+totalDBL+(totalTPL*2)+(totalHR*3))/totalAB
####        newOBP = (totalH+totalBB)/(totalAB+totalBB+totalSF+totalS)
####
####        oldOPS = oldSLG+oldOBP
####        newOPS = newSLG+newOBP
####        
####
####        maxAVG.append(newAVG - oldAVG)
####        maxOPS.append(newOPS - oldOPS)
####
####        
####    print(year, oldOPS, max(maxOPS))
##
##
##
##
##
##
##
##
##abNum = 190
##batters = []
##
##cmd = "SELECT DISTINCT battingStats.playerId FROM battingStats WHERE playerId NOT IN ( SELECT DISTINCT playerId FROM pitchingStats)"
##curs.execute(cmd)
##players = [x[0] for x in curs.fetchall()]
##
##for playerId in players:
##    try:
##        cmd = "SELECT firstName, lastName FROM players WHERE playerId = {}"
##        curs.execute(cmd.format(playerId))
##        firstName, lastName = curs.fetchone()
##
##        print(firstName, lastName)
##
##        
##        player = {"firstName": firstName, "lastName": lastName, "playerId": playerId}
##
##        
##        for year in (2015,2016,2017):
##            cmd = "SELECT ((SUM(bb) * {0})/ SUM(ab)), ((SUM(h) * {0})/ SUM(ab)), ((SUM(dbl) * {0})/ SUM(ab)), ((SUM(tpl) * {0})/ SUM(ab)), ((SUM(hr) * {0})/ SUM(ab)), ((SUM(sf) * {0})/ SUM(ab)), ((SUM(s) * {0})/ SUM(ab)) from battingStats, games WHERE games.gameId = battingStats.gameId AND games.season = {1} AND battingStats.playerId NOT IN ( SELECT DISTINCT pitchingStats.playerId FROM pitchingStats)"
##            curs.execute(cmd.format(abNum, year))
##            bbNum, hNum, dblNum, tplNum, hrNum, sfNum, sNum = curs.fetchone()
##
##                        
##            cmd = "SELECT SUM(ab), SUM(bb), SUM(r), SUM(h), SUM(dbl), SUM(tpl), SUM(hr), SUM(rbi), SUM(sb), SUM(sf), SUM(s) FROM battingStats, players, games WHERE battingStats.playerId = players.playerId AND battingStats.playerId = {} AND battingStats.gameId = games.gameId AND games.season = {} GROUP BY battingStats.playerId"
##            curs.execute(cmd.format(playerId,year))
##        
##            ab, bb, r, h, dbl, tpl, hr, rbi, sb, sf, s = curs.fetchone()
##            stats = {"score": 0}
##            statConvert = {"r":r, "h":h, "hr":hr, "rbi":rbi, "sb":sb}
##
##            totalAB = abNum + (ab/24.0)
##            totalBB = bbNum + (bb/24.0)
##            totalH = hNum + (h/24.0)
##            totalDBL = dblNum + (dbl/24.0)
##            totalTPL = tplNum + (tpl/24.0)
##            totalHR = hrNum + (hr/24.0)
##            totalSF = sfNum + (sf/24.0)
##            totalS = sNum + (s/24.0)
##                       
##            for stat in ("r", "h", "hr", "rbi", "sb", "tb", "avg", "ops"):
##                maxNum = None
##                with open(filePath+stat) as fileIn:
##                    for line in fileIn:
##                        lineYear, num = line.split()
##                        if int(lineYear) == year:
##                            maxNum = num
##
##                if stat == "avg":
##                    num = (totalH/totalAB) - (hNum/abNum)
##                    stats[stat] = 10 * num / float(maxNum)
##
##                elif stat == "ops":
##                    oldSLG = (hNum+dblNum+(tplNum*2)+(hrNum*3))/190
##                    oldOBP = (hNum+bbNum)/(abNum+bbNum+sfNum+sNum)
##
##                    newSLG = (totalH+totalDBL+(totalTPL*2)+(totalHR*3))/totalAB
##                    newOBP = (totalH+totalBB)/(totalAB+totalBB+totalSF+totalS)
##
##                    num = (newSLG+newOBP) - (oldSLG+oldOBP)
##                    stats[stat] = 10 * num/float(maxNum)
##                    
##                elif stat == "tb":
##                    stats[stat] = 10 * float(h+dbl+tpl*2+hr*3) / float(maxNum)
##                else:
##                    stats[stat] = 10 * statConvert[stat] / float(maxNum)
##
##                stats["score"] = stats["score"] + stats[stat]
##            player[year] = stats
##        batters.append(player)
##    except TypeError:
##            pass
##
##for player in batters:
##    pprint(player)
##
##    print("\n\n\n")  
##        
##with open("/home/ededub/FEFelson/MLB/batters.json", "w") as fileOut:
##    dump({"batters":batters}, fileOut)

##pos = "OF"
##with open(filePath+pos, "w") as fileOut:
##    cmd = "SELECT players.playerId, firstName, lastName FROM players, positions, games WHERE games.gameId = positions.gameId AND players.playerId = positions.playerId AND games.season = 2017 AND (positions.position = 'LF' OR positions.position = 'CF' OR positions.position = 'RF') GROUP BY positions.playerId HAVING (COUNT(positions.position = 'LF') + COUNT(positions.position = 'CF') + COUNT(positions.position = 'RF'))   > 10"
##    curs.execute(cmd.format(pos))
##    for player in curs.fetchall():
##        print(player)
##        fileOut.write(player[0]+"\n")
pos = ("LF","CF","RF")
cmd = "SELECT COUNT(positions.game_id) FROM positions INNER JOIN games ON games.game_id = positions.game_id WHERE player_id = ? AND position IN {} AND season = ?"
print(cmd.format(str(pos)))
curs.execute(cmd.format(str(pos)), (34986,2018))
print(curs.fetchone())
        

conn.close()
