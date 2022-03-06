import datetime
import wx

from copy import deepcopy

from .. import Environ as ENV

awayHome = ("away", "home")
awayHomeDict = dict([(label, {}) for label in awayHome])


class TitlePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        teamFont = wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        pitchFont = wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        lineFont = wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        recordFont = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)


        self.values = awayHomeDict

        self.gameDate = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.gameDate.SetFont(recordFont)

        self.gameTime = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.gameTime.SetFont(recordFont)


        self.oddsPanel = wx.Panel(self, size=((80,80)), style=wx.BORDER_SIMPLE)
        self.hAbrv = wx.StaticText(self.oddsPanel)
        self.hAbrv.SetFont(lineFont)

        self.spread = wx.StaticText(self.oddsPanel)
        self.spread.SetFont(lineFont)

        self.ou = wx.StaticText(self.oddsPanel)
        self.ou.SetFont(lineFont)

        tagSizers = {}
        for hA in awayHome:
            haTag = wx.StaticText(self, size=(50,20), style=wx.ALIGN_CENTRE_HORIZONTAL)
            haTag.SetForegroundColour(wx.WHITE)
            if hA == "home":
                haTag.SetBackgroundColour(wx.Colour("sea green"))
            else:
                haTag.SetBackgroundColour(wx.BLUE)
            self.values[hA]["hATag"] = haTag
            haTag.Hide()

            tFTag = wx.StaticText(self, size=(70,20), style=wx.ALIGN_CENTRE_HORIZONTAL)
            tFTag.SetForegroundColour(wx.WHITE)
            tFTag.SetBackgroundColour(wx.Colour("ORCHID"))
            self.values[hA]["tFTag"] = tFTag

            oDTag = wx.StaticText(self, size=(70,20), style=wx.ALIGN_CENTRE_HORIZONTAL)
            oDTag.SetForegroundColour(wx.WHITE)
            oDTag.SetBackgroundColour(wx.BLACK)
            self.values[hA]["oDTag"] = oDTag

            wLTag = wx.StaticText(self, size=(70,20), style=wx.ALIGN_CENTRE_HORIZONTAL)
            wLTag.SetForegroundColour(wx.BLACK)
            wLTag.SetBackgroundColour(wx.Colour("yellow"))
            wLTag.Hide()
            self.values[hA]["wLTag"] = wLTag




            b2bTag = wx.StaticText(self, label="B2B", size=(50,20), style=wx.ALIGN_CENTRE_HORIZONTAL)
            b2bTag.SetForegroundColour(wx.WHITE)
            b2bTag.SetBackgroundColour(wx.RED)
            b2bTag.Hide()
            self.values[hA]["b2b"] = b2bTag

            hATagSizer = wx.BoxSizer()
            hATagSizer.Add(b2bTag, 0, wx.RIGHT | wx.GROW, 5)
            hATagSizer.Add(haTag, 0, wx.RIGHT | wx.GROW, 5)
            hATagSizer.Add(oDTag, 0, wx.RIGHT | wx.GROW, 5)
            hATagSizer.Add(tFTag, 0, wx.RIGHT | wx.GROW, 5)


            tagSizers[hA] = hATagSizer


            money = wx.StaticText(self.oddsPanel)
            money.SetFont(lineFont)
            self.values[hA]["moneyLine"] = money

            record = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL)
            record.SetFont(recordFont)
            self.values[hA]["record"] = record

            name = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL)
            name.SetFont(teamFont)
            self.values[hA]["name"] = name

            logo = wx.StaticBitmap(self)
            self.values[hA]["logo"] = logo


        oddSizer = wx.BoxSizer(wx.VERTICAL)
        oddSizer.Add(self.hAbrv, 1, wx.CENTER)
        oddSizer.Add(self.spread, 1, wx.CENTER)
        oddSizer.Add(self.ou, 1, wx.CENTER)
        splitSizer = wx.BoxSizer()
        [splitSizer.Add(self.values[hA]["moneyLine"], 1, wx.ALL, 5) for hA in awayHome]
        oddSizer.Add(splitSizer, 1, wx.CENTER)
        self.oddsPanel.SetSizer(oddSizer)


        hASizers = {}
        for hA in awayHome:
            teamSizer = wx.BoxSizer(wx.VERTICAL)
            halfSizer = wx.BoxSizer()
            leftSizer = wx.BoxSizer(wx.VERTICAL)
            leftSizer.Add(self.values[hA]["logo"], 0, wx.CENTER)
            # leftSizer.Add(wLTag, 0, wx.ALL, 10)

            rightSizer = wx.BoxSizer(wx.VERTICAL)
            rightSizer.Add(self.values[hA]["name"], 0, wx.CENTER | wx.BOTTOM, 15)
            rightSizer.Add(self.values[hA]["record"], 0, wx.CENTER | wx.BOTTOM, 50)
            halfSizer.Add(leftSizer, 0)
            halfSizer.Add(rightSizer, 0)

            teamSizer.Add(halfSizer, 1, wx.BOTTOM, 20)
            teamSizer.Add(tagSizers[hA], 0, wx.CENTER)

            hASizers[hA] = teamSizer

        midSizer = wx.BoxSizer(wx.VERTICAL)
        midSizer.Add(self.gameDate, 0, wx.EXPAND)
        midSizer.Add(self.gameTime, 0, wx.EXPAND | wx.BOTTOM, 10)
        midSizer.Add(self.oddsPanel, 0)

        mainSizer = wx.BoxSizer()
        mainSizer.Add(hASizers["away"], 1, wx.RIGHT, 20)
        mainSizer.Add(midSizer, 0, wx.EXPAND)
        mainSizer.Add(hASizers["home"], 1, wx.LEFT, 20)

        self.SetSizer(mainSizer)




class BaseballTitlePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        teamFont = wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        pitchFont = wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        lineFont = wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        recordFont = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        self.gameDate = wx.StaticText(self)
        self.gameDate.SetFont(recordFont)

        self.gameTime = wx.StaticText(self)
        self.gameTime.SetFont(recordFont)

        self.logos = {}
        self.teamNames = {}
        self.teamRecords = {}
        self.starters = {}
        self.startStats = {}

        self.oddsPanel = wx.Panel(self, size=((80,80)), style=wx.BORDER_SIMPLE)
        self.oddsPanel.SetBackgroundColour(wx.WHITE)
        self.hAbrv = wx.StaticText(self.oddsPanel)
        self.hAbrv.SetFont(lineFont)

        self.spread = wx.StaticText(self.oddsPanel)
        self.spread.SetFont(lineFont)

        self.ou = wx.StaticText(self.oddsPanel)
        self.ou.SetFont(lineFont)

        self.line = {}
        self.money = {}




        for hA in awayHome:

            line = wx.StaticText(self.oddsPanel)
            line.SetFont(lineFont)

            money = wx.StaticText(self.oddsPanel)
            money.SetFont(lineFont)

            record = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL)
            record.SetFont(recordFont)

            name = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL)
            starter = wx.StaticText(self)
            startStats = wx.StaticText(self)
            startStats.SetFont(lineFont)
            name.SetFont(teamFont)
            starter.SetFont(pitchFont)
            self.teamNames[hA] = name
            self.starters[hA] = starter

            logo = wx.StaticBitmap(self)
            self.logos[hA] = logo

            self.line[hA] = line
            self.money[hA] = money

            self.teamRecords[hA] = record
            self.startStats[hA] = startStats



        mainSizer = wx.BoxSizer()
        midSizer = wx.BoxSizer(wx.VERTICAL)


        sizers = {}
        for hA in awayHome:
            sizer = wx.BoxSizer(wx.VERTICAL)
            logoSizer = wx.BoxSizer()
            textSizer = wx.BoxSizer(wx.VERTICAL)
            textSizer.Add(self.teamNames[hA], 0, wx.CENTER)
            textSizer.Add(self.teamRecords[hA], 0, wx.CENTER)

            logoSizer.Add(self.logos[hA],0, wx.CENTER)
            logoSizer.Add(textSizer, 1)

            sizer.Add(logoSizer,0, wx.CENTER)
            sizer.Add(self.starters[hA],0, wx.CENTER)
            sizer.Add(self.startStats[hA],0,wx.CENTER)

            sizers[hA] = sizer

        oddSizer = wx.BoxSizer(wx.VERTICAL)
        oddSizer.Add(self.hAbrv, 1, wx.CENTER)
        oddSizer.Add(self.spread, 1, wx.CENTER)
        oddSizer.Add(self.ou, 1, wx.CENTER)
        splitSizer = wx.BoxSizer()
        for hA in awayHome:
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.line[hA], 1, wx.BOTTOM, 5)
            sizer.Add(self.money[hA])
            splitSizer.Add(sizer, 1, wx.ALL, 5)
        oddSizer.Add(splitSizer, 1, wx.CENTER)

        self.oddsPanel.SetSizer(oddSizer)

        midSizer.Add(self.gameDate,0,wx.CENTER)
        midSizer.Add(self.gameTime,0,wx.CENTER)
        midSizer.Add(self.oddsPanel, 1, wx.EXPAND)

        mainSizer.Add(sizers["away"], 1, wx.EXPAND)
        mainSizer.Add(midSizer, 0, wx.CENTER)
        mainSizer.Add(sizers["home"], 1, wx.EXPAND)




        self.SetSizer(mainSizer)


    def setPanel(self, game):
        gd = datetime.datetime.strptime(game["gameTime"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=4)
        self.gameDate.SetLabel(gd.strftime("%a %b %d"))
        self.gameTime.SetLabel(gd.strftime("%I:%M %p"))
        self.hAbrv.SetLabel(game["data"]["teams"]["home"]["abrv"].upper())
        for hA in awayHome:
            team = game["data"]["teams"][hA]
            name = "{} {}".format(team["firstName"], team["lastName"])

            self.teamNames[hA].SetLabel(name)

            try:
                logo = wx.Image(ENV.logoPath.format(game["leagueId"], game["{}Id".format(hA)]), wx.BITMAP_TYPE_PNG).Scale(50, 50, wx.IMAGE_QUALITY_HIGH)
            except:
                logo = wx.Image(ENV.logoPath.format(game["leagueId"], -1), wx.BITMAP_TYPE_PNG).Scale(35, 35, wx.IMAGE_QUALITY_HIGH)

            logo = logo.ConvertToBitmap()
            self.logos[hA].SetBitmap(logo)

        try:
            odds = game["odds"][-1]["101"]

            try:
                spread = odds["home_spread"] if float(odds["home_spread"]) < 0 else "+"+str(odds["home_spread"])
            except:
                spread = ""
            self.spread.SetLabel("{}".format(spread))
            self.ou.SetLabel("{}".format(odds["total"]))
            for hA in awayHome:
                try:
                    line = odds["{}_line".format(hA)] if int(odds["{}_line".format(hA)]) < 0 else "+"+str(odds["{}_line".format(hA)])
                    money = odds["{}_ml".format(hA)] if int(odds["{}_ml".format(hA)]) < 0 else "+"+str(odds["{}_ml".format(hA)])
                except:
                    line = ''
                    money = ''
                self.line[hA].SetLabel(line)
                self.money[hA].SetLabel(money)
        except:
            pass
