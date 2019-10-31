from SportsDB.WebService.Yahoo.FantasyAPI import FantasyAPI

baseUrl = "https://fantasysports.yahooapis.com/fantasy/v2/league/mlb.l.{}"

api = FantasyAPI()

##for leagueId in (84634, 52353):
##
##    path = "MLB/{}/metadata.xml".format(leagueId)
##    url = baseUrl.format(leagueId)
##    api.getPage(url, path)
##
##    path = "MLB/{}/settings.xml".format(leagueId)
##    url = baseUrl.format(leagueId)+"/settings"
##    api.getPage(url, path)
##
##    path = "MLB/{}/teams.xml".format(leagueId)
##    url = baseUrl.format(leagueId)+"/teams"
##    api.getPage(url, path)
##
##    path = "MLB/{}/players.xml".format(leagueId)
##    url = baseUrl.format(leagueId)+"/players"
##    api.getPage(url, path)
####
##    path = "MLB/{}/draftresults.xml".format(leagueId)
##    url = baseUrl.format(leagueId)+"/draftresults"
##    api.getPage(url, path)
##
##    path = "MLB/{}/transactions.xml".format(leagueId)
##    url = baseUrl.format(leagueId)+"/transactions"
##    api.getPage(url, path)   

##for i in range(0,400,25):
##    path = "MLB/players{}.xml".format(i)
##    url = baseUrl.format(84634)+"/players;start={}".format(i)
##    api.getPage(url, path)

##
url = "https://fantasysports.yahooapis.com/fantasy/v2/game/mlb"
path = "MLB/leagues.xml"
resp = api.getPage(url, path)



##leagueId = 55376
##path = "MLB/transactions.xml".format(leagueId)
##url = baseUrl.format(leagueId)+"/transactions"
##api.getPage(url, path)  
