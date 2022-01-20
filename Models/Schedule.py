import datetime

from .. import Environ as ENV
from ..Interfaces import Downloadable
from ..Utils.ResultsParse import yId

from pprint import pprint

################################################################################
################################################################################






################################################################################
################################################################################


class Schedule(Downloadable):

    _info = {"games":[]}
    _url = ENV.schedUrl

    def __init__(self, league, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.league = league


    def getGames(self, gameDate):
        print("Schedule get games")
        games = []
        self.setUrl(gameDate)
        self.info = self._info.copy()
        self.parseData()
        for game in [game for game in sorted(self.info["games"].values(), key=lambda x:  datetime.datetime.strptime(x["gameTime"], "%a, %d %b %Y %H:%M:%S %z")) if game["status"] == "final"]:
            if self.isValid(gameDate, game):
                games.append(game)
        return games


    def getMatchup(self, gameDate):
        games = []
        self.setUrl(gameDate)
        self.info = self._info.copy()
        self.parseData()
        for game in [game for game in sorted(self.info["games"].values(), key=lambda x:  datetime.datetime.strptime(x["gameTime"], "%a, %d %b %Y %H:%M:%S %z")) if game["status"] == "pregame"]:
            games.append(game)
        return games


    def isValid(self, gameDate, game):
        raise AssertionError



    def parseData(self):
        self.info["games"] = {}
        stores = self.downloadItem()
        # pprint(stores)
        pageData = stores["PageStore"]["pageData"]["entityData"]
        leagueAbrv = pageData["leagueId"]
        queryData = stores["ClientStore"]["currentRoute"]["query"]
        gamesData = stores["GamesStore"]["games"]
        for game in [value for key, value in gamesData.items() if leagueAbrv in key and value["season_phase_id"] != "season.phase.preseason"]:
            gameDate = datetime.datetime.strptime(game["start_time"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)
            _, month, day = str(gameDate.date()).split("-")


            newGame = {
                        "gameId": -1,
                        "gameTime": None,
                        "leagueId": None,
                        "homeId": -1,
                        "awayId": -1,
                        "url": None,
                        "season": -1,
                        "week": -1,
                        "month": -1,
                        "day": -1,
                        "seasonPhase": -1,
                        "players": {"away":{}, "home":{}},
                        "odds":{},
                        "injuries":{},

                        }


            newGame["leagueId"] = leagueAbrv
            newGame["awayId"] = yId(game["away_team_id"])
            newGame["awayPoints"] = game["total_away_points"]
            newGame["homeId"] = yId(game["home_team_id"])
            newGame["homePoints"] = game["total_home_points"]
            newGame["gameId"] = yId(game["gameid"])
            newGame["gameTime"] = game["start_time"]
            newGame["status"] = game["status_type"]
            newGame["seasonPhase"] = game["season_phase_id"]
            newGame["odds"] = game.get("odds",{}),
            newGame["season"] = game["season"]
            newGame["week"] = game.get("week_number", -1)
            newGame["month"] = month
            newGame["day"] = day

            try:
                newGame["url"] = "https://sports.yahoo.com" + game["navigation_links"]["boxscore"]["url"]
            except (KeyError, TypeError):
                newGame["url"] = None
            self.info["games"][game["gameid"]] = newGame
        # pprint(self.info)



################################################################################
################################################################################


class DailySchedule(Schedule):


    def __init__(self, leagueInfo, *args, **kwargs):
        super().__init__(leagueInfo, *args, **kwargs)


    def isValid(self, gameDate, game):
        gameDate = datetime.date.fromisoformat(gameDate)
        result = True
        if datetime.date.fromisoformat(self.league.fileManager.info["allStar"]) == gameDate:# or (datetime.datetime.strptime(game["gameTime"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)).date() != gameDate:
            result = False
        return result


    def setUrl(self, gameDate):
        print("Setting Daily Schedule URL")
        gameDate = str(gameDate)
        slugId = self.league.fileManager.info["slugId"]
        schedState = 2
        if datetime.date.fromisoformat(self.league.fileManager.info["playoffs"]) <= datetime.date.fromisoformat(gameDate):
            schedState = 3
        self.url = self._url.format({"slugId":slugId, "schedState":"", "dateRange":str(gameDate)})
        print(self.url,"\n")



################################################################################
################################################################################


class WeeklySchedule(Schedule):


    def __init__(self, leagueInfo, *args, **kwargs):
        super().__init__(leagueInfo, *args, **kwargs)


    def isValid(self, gameDate, game):
        result = True
        # if datetime.date.fromisoformat(self.leagueInfo["allStar"]) == gameDate:
        #     result = False
        return result


    def setUrl(self, gameDate):

        slugId = self.league.fileManager.info["slugId"]
        schedState = 2

        # if datetime.date.fromisoformat(self.leagueInfo["playoffs"]) <= gameDate:
        #     schedState = 3
        week = self.league.fileManager.getWeek(gameDate)
        self.url = self._url.format({'slugId':slugId, 'schedState':schedState, 'dateRange':str(week)})
