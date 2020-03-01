import wx

import FelsonSports.Views.GamePanels.TeamShotsPanel as TSP

from pprint import pprint

class TeamShotsControl:

    def __init__(self, parentView):

        self.game = None
        self.panel = TSP.TeamShotsPanel(parentView)

        self.panel.optionBox.Bind(wx.EVT_COMBOBOX, self.update)


    def getPanel(self):
        return self.panel


    def setGame(self, game):
        self.game = game
        self.update()


    def update(self, evt=None):

        homeTeam = self.game.getTeam("home")
        awayTeam = self.game.getTeam("away")

        if self.game.hasPlayed:

            awayShot = dict(zip(range(1,11), [self.game.getTeamStats("away", "shots_{}".format(box)) for box in range(1,11)]))
            homeShot = dict(zip(range(1,11), [self.game.getTeamStats("home", "shots_{}".format(box)) for box in range(1,11)]))
            pprint(awayShot)
            for box in range(1,11):
                if self.panel.optionBox.GetStringSelection() == "fg":
                    self.panel.awayChart.mainBoxes[box].SetLabel("{}-{} {}%".format(awayShot["fga"], awayShot["fgm"], int(100*(awayShot["fgm"]/awayShot["fga"]))))
                    self.panel.homeChart.mainBoxes[box].SetLabel("{}-{} {}%".format(homeShot["fga"], homeShot["fgm"], int(100*(homeShot["fgm"]/homeShot["fga"]))))
                else:
                    self.panel.awayChart.mainBoxes[box].SetLabel("{} {}%".format(awayShot["pts"], int(100*(awayShot["pts"]/sum(awayShot.values())))))
                    self.panel.homeChart.mainBoxes[box].SetLabel("{} {}%".format(homeShot["pts"], int(100*(homeShot["pts"]/sum(homeShot.values())))))

            awayShot = dict(zip(range(1,11), [self.game.getTeam("away").getStats("shots_team", box) for box in range(1,11)]))
            homeShot = dict(zip(range(1,11), [self.game.getTeam("home").getStats("shots_team", box) for box in range(1,11)]))

            for box in range(1,11):
                if self.panel.optionBox.GetStringSelection() == "fg":
                    self.panel.awayChart.secondBoxes[box].SetLabel("{:.2f}-{:.2f} {}%".format(awayShot["fga"], awayShot["fgm"], int(100*(awayShot["fgm"]/awayShot["fga"]))))
                    self.panel.homeChart.secondBoxes[box].SetLabel("{:.2f}-{:.2f} {}%".format(homeShot["fga"], homeShot["fgm"], int(100*(homeShot["fgm"]/homeShot["fga"]))))
                else:
                    self.panel.awayChart.secondBoxes[box].SetLabel("{:.2f} {}%".format(awayShot["pts"], int(100*(awayShot["pts"]/sum(awayShot.values())))))
                    self.panel.homeChart.secondBoxes[box].SetLabel("{:.2f} {}%".format(homeShot["pts"], int(100*(homeShot["pts"]/sum(homeShot.values())))))


        else:

            awayShot = dict(zip(range(1,11), [self.game.getTeam("away").getStats("shots_team", box) for box in range(1,11)]))
            homeShot = dict(zip(range(1,11), [self.game.getTeam("home").getStats("shots_team", box) for box in range(1,11)]))

            for box in range(1,11):

                if self.panel.optionBox.GetStringSelection() == "fg":
                    self.panel.awayChart.mainBoxes[box].SetLabel("{:.2f}-{:.2f} {}%".format(awayShot[box]["fga"], awayShot[box]["fgm"], int(100*(awayShot[box]["fgm"]/awayShot[box]["fga"]))))
                    self.panel.homeChart.mainBoxes[box].SetLabel("{:.2f}-{:.2f} {}%".format(homeShot[box]["fga"], homeShot[box]["fgm"], int(100*(homeShot[box]["fgm"]/homeShot[box]["fga"]))))
                else:
                    self.panel.awayChart.mainBoxes[box].SetLabel("{:.2f} {}%".format(awayShot[box]["pts"], int(100*(awayShot[box]["pts"]/sum([awayShot[i]["pts"] for i in range(1,11)] )))))
                    self.panel.homeChart.mainBoxes[box].SetLabel("{:.2f} {}%".format(homeShot[box]["pts"], int(100*(homeShot[box]["pts"]/sum([homeShot[i]["pts"] for i in range(1,11)] )))))

            awayShot = dict(zip(range(1,11), [self.game.getTeam("away").getStats("shots_opp", box) for box in range(1,11)]))
            homeShot = dict(zip(range(1,11), [self.game.getTeam("home").getStats("shots_opp", box) for box in range(1,11)]))

            for box in range(1,11):
                if self.panel.optionBox.GetStringSelection() == "fg":
                    self.panel.awayChart.secondBoxes[box].SetLabel("{:.2f}-{:.2f} {}%".format(awayShot[box]["fga"], awayShot[box]["fgm"], int(100*(awayShot[box]["fgm"]/awayShot[box]["fga"]))))
                    self.panel.homeChart.secondBoxes[box].SetLabel("{:.2f}-{:.2f} {}%".format(homeShot[box]["fga"], homeShot[box]["fgm"], int(100*(homeShot[box]["fgm"]/homeShot[box]["fga"]))))
                else:
                    self.panel.awayChart.secondBoxes[box].SetLabel("{:.2f} {}%".format(awayShot[box]["pts"], int(100*(awayShot[box]["pts"]/sum([awayShot[i]["pts"] for i in range(1,11)])))))
                    self.panel.homeChart.secondBoxes[box].SetLabel("{:.2f} {}%".format(homeShot[box]["pts"], int(100*(homeShot[box]["pts"]/sum([homeShot[i]["pts"] for i in range(1,11)])))))

        self.panel.awayChart.Layout()
        self.panel.homeChart.Layout()
        self.panel.Layout()
