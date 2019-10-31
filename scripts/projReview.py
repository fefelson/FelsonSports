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


def fix(x):
    x = 0 if x == None else x
    return x

pitchStatsAbrv = ("ip", "w", "era", "whip", "k9")
batStatsAbrv = ("ab", "sing", "dbl", "tpl", "hr")


fanDB = DB.MLBDFS()
fanDB.openDB()


sheetId = 40

##gameIds = [x[0] for x in fanDB.fetchAll("SELECT DISTINCT game_id FROM dk_sheet_games")]
##
##
##playerInfo = mlbDB.fetchAll("SELECT bs.game_id, bs.player_id, first_name, last_name, team.abrv, opp.abrv, total FROM ( {} ) AS bs INNER JOIN pro_players ON bs.player_id = pro_players.player_id INNER JOIN pro_teams AS team ON bs.team_id = team.team_id INNER JOIN pro_teams AS opp ON bs.opp_id = opp.team_id WHERE bs.game_id in {} ORDER BY total DESC".format(batScoreCmd.format({"whrPlayerCmd":"", "andPlayerCmd":"", "gdCmd":getGDCmd(season=2019)}), tuple(gameIds)) )
##X = []
##Y = []
##for player in playerInfo:
####    try:
####        price, pos = fanDB.fetchOne("SELECT price, pos FROM dk_prices INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id WHERE game_id = ? AND yahoo_id = ?",player[:2] )
####    except TypeError:
####        price = "-1"
####        pos = "-1"
######    print("{:<8}{:.2f} {:<8}    {:<15}{:<15}  {}  {}".format(str(price), player[-1],pos, player[2], player[3], player[4], player[5]))
##    try:
##        price = fanDB.fetchItem("SELECT price FROM dk_prices INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id WHERE pos = '3B' AND price >= 4400 AND price <= 4900 AND game_id = ? AND yahoo_id = ?",player[:2])
##        X.append(price)
##        Y.append(player[-1])
##        
##    except TypeError:
##        pass
##
##print("Total - {}   {:.1f}%".format(len(Y), (sum([int(x >= 20) for x in Y])/len(Y))*100))
##raise AssertionError
##print(numpy.corrcoef(X,Y))
##plt.scatter(X,Y)
##plt.show()
##raise AssertionError




gameIds = [x[0] for x in fanDB.fetchAll("SELECT game_id FROM dk_sheet_games WHERE dk_sheet_id = ?",(sheetId,))]
gameDate = fanDB.fetchOne("SELECT game_date FROM dk_sheets WHERE dk_sheet_id = ?",(sheetId,))[0].split("/")
gameDate = datetime.date(int(gameDate[-1]), int(gameDate[0]), int(gameDate[1]))



players = {"P":[],
            "C":[],
            "1B":[],
               "2B":[],
               "3B":[],
               "SS":[],
               "OF":[]}



    
                             
for gameId in gameIds:
    with open(ENV.getPath("matchup", fileName=gameId, gameDate=gameDate)) as fileIn:
        info = json.load(fileIn)

        try:        
            for team, opp in (("home","away"),("away","home")):
                for player in info["teams"][opp]["players"]:
                    if player["playerType"] == "pitcher":
                        starter = player
                        break
                try:
                    price = fanDB.fetchItem("SELECT price FROM dk_prices INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id INNER JOIN dk_sheet_players ON dk_prices.dk_price_id = dk_sheet_players.dk_price_id WHERE yahoo_id = ? AND dk_sheet_id = ?",(info["teams"][opp]["starter"],sheetId))
                except TypeError:
                    price = -1
                starter["price"] = price
        
                print("\n\n\nStarter {}\n".format(info["teams"][opp]["abrv"]))
                print("{:<3}{:<7}{:<10}{}".format(starter["throws"],str(price),starter["firstName"], starter["lastName"]))

                
                
                timeStats = [fix(starter["stats"]["stats"]["season"][stat]) for stat in pitchStatsAbrv] 

                print("\n\t            ip   w   era     whip    k9")   
                print("\n\tSeason    {:3.0f}   {:2.0f}   {:2.2f}    {:2.2f}    {:2.2f}".format(*timeStats))

                timeStats = [fix(starter["stats"]["stats"]["month"][stat]) for stat in pitchStatsAbrv] 
        
                print("\tMonth     {:3.0f}   {:2.0f}   {:2.2f}    {:2.2f}    {:2.2f}".format(*timeStats))

                timeStats = [fix(starter["stats"]["statsVsTeam"]["season"][stat]) for stat in pitchStatsAbrv] 
        
                print("\n\tvs {}     {:3.0f}   {:.0f}   {:.2f}    {:.2f}    {:.2f}".format(info["teams"][team]["abrv"], *timeStats))

                monthPts = fix(starter["stats"]["pts"]["month"]["pts"])
                seasonPts = fix(starter["stats"]["pts"]["season"]["pts"])
                try:
                    print("\n\tAvg  {:.2f}    {:.1f}%".format(monthPts, ((monthPts-seasonPts)/seasonPts)*100))
                except ZeroDivisionError:
                    print("\n\tAvg  No games")
                teamPts = fix(starter["stats"]["ptsVsTeam"]["season"]["pts"])
                try:
                    print("\tAvg vs {}  {:.2f}    {:.1f}%".format(info["teams"][team]["abrv"], teamPts, ((teamPts-seasonPts)/seasonPts)*100))
                except ZeroDivisionError:
                    print("\n\tAvg vs  No games")
                    
                seasonAvg = fix(starter["stats"]["ptsVsAll"]["season"]["pts"])
                monthAvg = fix(starter["stats"]["ptsVsAll"]["month"]["pts"])
                
                try:
                    print("\n\tAll vs {}  {:.2f}    {:.1f}%".format(info["teams"][team]["abrv"], monthAvg, ((monthAvg-seasonAvg)/seasonAvg)*100))
                except ZeroDivisionError:
                    print("\n\tAvg  vs {}   No games".format(info["teams"][team]["abrv"]))

                seasonAvg = fix(starter["stats"]["ptsVsThrows"]["season"]["pts"])
                monthAvg = fix(starter["stats"]["ptsVsThrows"]["month"]["pts"])

                print("\t{} vs {} {:.2f}    {:.1f}%".format(starter["throws"], info["teams"][team]["abrv"], monthAvg, (((monthAvg-seasonAvg)/seasonAvg)*100)))

                try:
                    print("\n\t$ per pt {:.2f}".format(price/monthPts))
                except ZeroDivisionError:
                    print("\n\t$ per pt   No pts")
                          

                print("\n\nBatters {}\n".format(info["teams"][team]["abrv"]))
                for batterId in [x[1] for x in info["teams"][team]["lineup"]]:
                    for player in info["teams"][team]["players"]:
                        if int(player["playerId"]) == int(batterId):
                            batter = player
                            break
                    try:
                        price, pos = fanDB.fetchOne("SELECT price, pos FROM dk_prices INNER JOIN dk_yahoo ON dk_prices.dk_id = dk_yahoo.dk_id INNER JOIN dk_sheet_players ON dk_prices.dk_price_id = dk_sheet_players.dk_price_id WHERE yahoo_id = ? AND dk_sheet_id = ?",(batter["playerId"],sheetId))
                    except TypeError:
                        price = -1
                        pos = "N/A"
                      
                    batter["price"] = price
                    print("{:<3}{:<7}{:<7}{:<10}{}".format(batter["bats"],str(price),pos,batter["firstName"], batter["lastName"]))
                    try:
                        print("\n\t              ab   r    hr   rbi   sb   avg   ops")
                        ab, r, h, hr, rbi, sb, tb = [fix(batter["stats"]["stats"]["season"][stat]) for stat in ("ab", "r", "h", "hr", "rbi", "sb", "tb")]

                        try:
                          print("\tSeason        {:3.0f}   {:2.0f}   {:2.0f}    {:3.0f}   {:2.0f}   {:.3f}    {:.3f}".format(ab, r, hr, rbi, sb, h/ab, tb/ab))
                        except ZeroDivisionError:
                          print("\tSeason        No AtBats")

                        ab, r, h, hr, rbi, sb, tb = [fix(batter["stats"]["stats"]["month"][stat]) for stat in ("ab", "r", "h", "hr", "rbi", "sb", "tb")]

                        try:
                          print("\tMonth        {:3.0f}   {:2.0f}   {:2.0f}    {:3.0f}   {:2.0f}   {:.3f}    {:.3f}".format(ab, r, hr, rbi, sb, h/ab, tb/ab))
                        except ZeroDivisionError:
                          print("\tMonth        No AtBats")

                        ab, sing, dbl, tpl, hr = [fix(batter["stats"]["statsVsPitcher"]["career"][stat]) for stat in batStatsAbrv]

                        tb = sing+(dbl*2)+(tpl*3)+(hr*4)

                        
                        try:
                            print("\n\tvs Pitcher\t\t{:.0f}   {:.1f}%   {:.3f}   {:.3f}".format(ab, (hr/ab)*100, (sing+dbl+tpl+hr)/ab, tb/ab))
                        except ZeroDivisionError:
                            print("\n\tvs Pitcher\t\tNo At Bats")
                    

                        ab, sing, dbl, tpl, hr = [fix(batter["stats"]["statsVsThrows"]["season"][stat]) for stat in batStatsAbrv]
                        tb = sing+(dbl*2)+(tpl*3)+(hr*4)
                        try:
                            print("\n\tSeason vs {}\t\t{:.0f}   {:.1f}%   {:.3f}   {:.3f}".format(starter["throws"], ab, (hr/ab)*100, (sing+dbl+tpl+hr)/ab, tb/ab))
                        except ZeroDivisionError:
                            print("\n\tSeason vs {}\t\tNo AtBats".format(starter["throws"]))

                        ab, sing, dbl, tpl,  hr = [fix(batter["stats"]["statsVsThrows"]["month"][stat]) for stat in batStatsAbrv]
                        tb = sing+(dbl*2)+(tpl*3)+(hr*4)
                        try:
                            print("\tMonth vs {}\t\t{:.0f}   {:.1f}%   {:.3f}   {:.3f}".format("throws", ab, (hr/ab)*100, (sing+dbl+tpl+hr)/ab, tb/ab))
                        except ZeroDivisionError:
                            print("\n\Month vs {}\t\tNo AtBats".format(starter["throws"]))

                        monthPts = fix(batter["stats"]["pts"]["month"]["pts"])
                        seasonPts = fix(batter["stats"]["pts"]["season"]["pts"])
                        try:
                            print("\n\tAvg  {:.2f}    {:.1f}%".format(monthPts, ((monthPts-seasonPts)/seasonPts)*100))
                        except ZeroDivisionError:
                            print("\n\tAvg   No At Bats")

                        monthPts = fix(batter["stats"]["ptsVsThrows"]["month"]["pts"])
                        seasonPts = fix(batter["stats"]["ptsVsThrows"]["season"]["pts"])
                        try:
                            print("\tAvg vs {}   {:.2f}    {:.1f}%".format(starter["throws"], monthPts, ((monthPts-seasonPts)/seasonPts)*100))
                        except ZeroDivisionError:
                            print("\tAvg vs {}    No At Bats".format(starter["throws"]))

                        teamPts = fix(batter["stats"]["ptsVsTeam"]["season"]["pts"])

                        try:
                            print("\tAvg vs {}  {:.2f}    {:.1f}%".format(info["teams"][opp]["abrv"], teamPts, ((teamPts-seasonPts)/seasonPts)*100))
                        except ZeroDivisionError:
                            pass
                        
                        try:
                            print("\n\t$ per pt {:.2f}".format(price/monthPts))
                        except ZeroDivisionError:
                            print("\n\t$ per pt   No pts")

                        print("\n\n\n")
                    except KeyError:
                        pass
          
                
                    
                
            print("\n\n\n")
        except KeyError:
            pass
        





fanDB.closeDB()
