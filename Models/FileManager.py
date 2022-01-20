import FelsonSports.Environ as ENV

from copy import deepcopy
from datetime import date, timedelta
from pprint import pprint

from ..Interfaces import Fileable, Updatable


################################################################################
################################################################################


class FileManager(Fileable, Updatable):


    def __init__(self, info, *args, **kwargs):
        super().__init__(info, *args, **kwargs)

        self.setFilePath(info)

        try:
            self.read()
        except FileNotFoundError:
            self.create(info)


    def create(self, info):
        print("Creating Sport")
        self.info = deepcopy(info)
        self.write()


    def setFilePath(self, info):
        print("set FileManager path", ENV.managerFilePath.format(info))
        self.filePath = ENV.managerFilePath.format(info)


    def update(self, newUpdate):
        print("FileManager lastUpdate = {}\n".format(newUpdate))
        #TODO: assert '{:4d}-{:2d}'
        self.info["lastUpdate"] = str(newUpdate)
        self.write()


    def determineMatchDate(self):
        print("Determining new daily matchdate\n")
        today = date.today()
        allStar = date.fromisoformat(self.info["allStar"])

        if today == allStar:
            today = None
        return today



################################################################################
################################################################################


class DailyFileManager(FileManager):

    def __init__(self, info, *args, **kwargs):
        super().__init__(info, *args, **kwargs)


    def checkUpdate(self):

        update = False
        today = date.today()
        lastUpdate = None

        lastUpdate = date.fromisoformat(self.info["lastUpdate"])

        print("Checking last update  {}  update = {}\n".format(lastUpdate, lastUpdate < today))
        if lastUpdate < today-timedelta(1):
            update = True
        return update


    def determineUpdates(self):
        print("Determining new daily updates\n")
        newUpdates = []
        today = date.today()
        lastUpdate = date.fromisoformat(self.info["lastUpdate"])
        allStar = date.fromisoformat(self.info["allStar"])

        while lastUpdate < today:
            if lastUpdate != allStar:
                newUpdates.append(str(lastUpdate))
            lastUpdate += timedelta(1)
        return newUpdates





################################################################################
################################################################################


class WeeklyFileManager(FileManager):

    def __init__(self, info, *args, **kwargs):
        super().__init__(info, *args, **kwargs)


    def checkUpdate(self):
        print("Checking for weekly update -- ", end="\t")
        # update = False
        # curWeek = -1
        # today = date.today()
        # lastUpdate = date.fromisoformat(self.info["lastUpdate"])
        # #yyyy-mm-dd
        # print(update)
        # print(lastUpdate.year, int(self.info["currentSeason"]), lastUpdate.year < int(self.info["currentSeason"]))
        # if lastUpdate.year < int(self.info["currentSeason"]):
        #     update = True
        # else:
        #     finalWeek = self.info["weeks"][-1]
        #
        #     upWeek = self.getWeek(lastUpdate)
        #
        #     # the final week has completed
        #     print(int(finalWeek[-1]), upWeek, lastUpdate.year, today, date.fromisoformat(finalWeek[1]))
        #
        #     if int(finalWeek[-1]) < upWeek and today > date.fromisoformat(finalWeek[1]):
        #         update = True
        #     else:
        #         print(upWeek, self.getWeek(today))
        #         if upWeek < self.getWeek(today):
        #             update = True
        #
        # print("Final Update", update)
        # raise
        return False

    def update(self, newUpdate):
        self.info["updateWeek"] = self.getWeek(newUpdate)
        super().update(newUpdate)


    def determineUpdates(self):
        print("determining weekly updates")
        newUpdates = []
        today = date.today()
        finalWeek = int(self.info["finalWeek"])
        todayWeek = self.getWeek(today)
        stopWeek = finalWeek+1 if todayWeek == -1 else todayWeek

        #yyyy-ww
        lastUpdate = date.fromisoformat(self.info["lastUpdate"])
        upYear = lastUpdate.year
        upWeek = self.getWeek(lastUpdate)

        if upYear < int(self.info["currentSeason"]):
            while upYear < int(self.info["currentSeason"]):
                while upWeek <= finalWeek and int(upWeek) != int(self.info["updateWeek"]):
                    newUpdates.append("{:4d}-{:d}".format(upYear, upWeek))
                    upWeek += 1
                upWeek = int(self.info["firstWeek"])
                upYear += 1

        while lastUpdate < today:
            newUpdates.append(lastUpdate)
            lastUpdate += timedelta(7)

        return newUpdates



    def getWeek(self, testDate):
        curWeek = -1
        # print("\n\ngetWeek")
        if not isinstance(testDate, date):
            testDate = date.fromisoformat(testDate)
        for startDay, endDay, weekNum in [(date.fromisoformat(week[0]), date.fromisoformat(week[1]), int(week[2])) for week in self.info["weeks"]]:
            # print(testDate, startDay, endDay, testDate > startDay, testDate < endDay)
            if testDate >= startDay and testDate <= endDay:
                curWeek = weekNum
                break
        # print(curWeek)
        return curWeek
