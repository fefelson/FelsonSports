import os

baseUrl = "https://sports.yahoo.com/{0[slugId]}/"
schedUrl = baseUrl+"scoreboard/?confId=all&schedState={0[schedState]}&dateRange={0[dateRange]}"
playerUrl = baseUrl + "players/{1}/"

# keys chosen to match downloaded json
homePath = os.environ["HOME"]+"/FEFelson/"
leaguePath = homePath + "{0[leagueId]}/"


dailyFile = leaguePath + "{0[season]}/{0[month]}/{0[day]}/"
weeklyFile = leaguePath + "{0[season]}/{0[week]}/"

dailyFilePath = dailyFile + "{0[gameId]}.json"
dailyMatchPath = dailyFile + "M{0[gameId]}.json"

weeklyFilePath = weeklyFile + "{0[gameId]}.json"
weeklyMatchPath = weeklyFile + "M{0[gameId]}.json"

managerFilePath =  leaguePath + ".manager.json"
playerFilePath = leaguePath + "Players/{1}.json"
reportFilePath = leaguePath + ".report.json"

dbPath = homePath + "{0}/{0}.db"
logoPath = homePath + "{}/logos/{}.png"

tarPath = homePath + "{}/{}.tar.gz"
tempDir = homePath + "{}/temp/"

tFFootballChoices = ("2Months", "Season", "1Month", "2Weeks")
tfBaseballChoices = ("1Month", "2Months", "Season", "2Weeks")
tFBasketballChoices = ("1Month", "2Weeks", "Season", "2Months", "PrvSeason")
