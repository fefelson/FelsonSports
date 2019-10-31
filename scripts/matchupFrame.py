import wx
from wx.lib.agw.shapedbutton import SButton

logoPath = "/home/ededub/FEFelson/MLB/Teams/Logos/{}.png"


class DKFrame(wx.Frame):

    def __init__(self):
        super().__init__(None)

        self.SetSize(wx.Size(550,700))

        self.mainPanel = wx.Panel(self)
        self.mainSizer = wx.BoxSizer()
        self.mainPanel.SetSizer(self.mainSizer)

        self.matchupPanel = MatchupPanel(self.mainPanel)
        self.teamPanel = TeamPanel(self.mainPanel, self)
        self.teamPanel.Hide()
      

        self.mainSizer.Add(self.matchupPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.teamPanel, 1, wx.EXPAND)


    def addMatchup(self, matchup):
        newPanel = GamePanel(self.matchupPanel, self, matchup)
        self.matchupPanel.sizer.Add(newPanel, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        for team in matchup.getTeams():
            self.teamPanel.addTeam(team)


    def newTeam(self, team):
        self.teamPanel.setTeam(team)
        self.matchupPanel.Hide()
        self.teamPanel.Show()
        self.mainPanel.Layout()



class PositionPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)


    def addTeam(self, team):
        pass

        
        


class SlotPanel(wx.Panel):

    def __init__(self, parent, abrv, slots):
        super().__init__(parent)

        self.abrv = abrv
        self.btns = []
        self.starters = []
        self.team = None

        self.index = 0

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)

        for i in range(slots):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            btn = SButton(self, i, label=self.abrv)
            btn.SetSize(wx.Size(100,100))
            btn.Bind(wx.EVT_BUTTON, self.btnClick)
            self.btns.append(btn)

            name = wx.StaticText(self)
            self.starters.append(name)
            sizer.Add(btn, 0)
            sizer.Add(name, 1)

            mainSizer.Add(sizer, 1)


        self.playerList = wx.ListBox(self)
        self.playerList.Bind(wx.EVT_LISTBOX_DCLICK, self.listClick)
        mainSizer.Add(self.playerList, 1)
        self.playerList.Hide()


    def btnClick(self, event):
        self.playerList.Hide() if self.playerList.IsShown() else self.playerList.Show()
        self.index = event.GetObject().GetId()
        self.GetParent().Layout()


        
            

            

        


class TeamPanel(wx.ScrolledWindow):

    def __init__(self, parent, mainFrame):
        super().__init__(parent)

        self.SetScrollbars(1, 1, 1, 1)
        self.SetScrollRate(1, 1)

        self.mainFrame = mainFrame
        self.teamList = []

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)

        self.teamBox = wx.ComboBox(self)
        self.teamBox.Bind(wx.EVT_COMBOBOX, self.onBox)
        mainSizer.Add(self.teamBox, 0, wx.EXPAND | wx.LEFT, wx.RIGHT, 15)

        self.sp = SlotPanel(self, "SP", 1)
        self.c = SlotPanel(self, "C", 1)
        self.fb = SlotPanel(self, "1B", 1)
        self.sb = SlotPanel(self, "2B", 1)
        self.tb = SlotPanel(self, "3B", 1)
        self.ss = SlotPanel(self, "SS", 1)
        self.of = SlotPanel(self, "OF", 3)


        for p in (self.sp, self.c, self.fb, self.sb, self.tb, self.ss, self.of):
            mainSizer.Add(p, 0, wx.EXPAND)


    def setTeam(self, team):
        for i,item in enumerate(self.teamBox.GetItems()):
            if item == team.getName():
                self.teamBox.SetSelection(i)
                break

        for panelPos in (self.sp, self.c, self.fb, self.sb, self.tb, self.ss, self.of):
            for teamPos in team.getPositions():
                if panelPos.abrv == teamPos.getAbrv():
                    if not teamPos.getStarters():
                        panelPos.starters[0].SetLabel("N/A")
                    for i, starter in enumerate(teamPos.getStarters()):
                        panelPos.starters[i].SetLabel(starter.getName())

                    panelPos.playerList.Clear()

                    for player in teamPos.getPlayers():
                        panelPos.playerList.Append(player.getName(), player)


    def addTeam(self, team):
        self.teamList.append(team)
        self.teamBox.Append(team.getName(), team)


    def onBox(self, event):
        team = self.teamBox.GetClientData(self.teamBox.GetSelection())
        self.setTeam(team)
        self.Layout()
        
        


class MatchupPanel(wx.ScrolledWindow):

    def __init__(self, parent):
        super().__init__(parent)

        self.SetScrollbars(1, 1, 1, 1)
        self.SetScrollRate(1, 1)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)



class GamePanel(wx.Panel):

    def __init__(self, parent, mainFrame, matchup):
        super().__init__(parent, style=wx.BORDER_SUNKEN)

        self.mainFrame = mainFrame

        self.awayTeam, self.homeTeam = matchup.getTeams()
        self.date = matchup.getDate()
        self.time = matchup.getTime()


        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)

        teamsPanel = wx.Panel(self)
        teamsSizer = wx.BoxSizer(wx.HORIZONTAL)
        teamsPanel.SetSizer(teamsSizer)
        
        detailsPanel = wx.Panel(self)
        detailsSizer = wx.BoxSizer(wx.VERTICAL)
        detailsPanel.SetSizer(detailsSizer)

        homePanel = wx.Panel(teamsPanel)
        homeSizer = wx.BoxSizer(wx.HORIZONTAL)
        homePanel.SetSizer(homeSizer)
        
        awayPanel = wx.Panel(teamsPanel)
        awaySizer = wx.BoxSizer(wx.HORIZONTAL)
        awayPanel.SetSizer(awaySizer)

        
        self.awayLabel = wx.StaticText(awayPanel, label=self.awayTeam.getName(), name="away")
        self.awayLabel.Bind(wx.EVT_LEFT_DCLICK, self.onClick)        
        self.homeLabel = wx.StaticText(homePanel, label=self.homeTeam.getName(), name="home")
        self.homeLabel.Bind(wx.EVT_LEFT_DCLICK, self.onClick)
        
        self.awayLogo = wx.StaticBitmap(awayPanel, bitmap= wx.Image(logoPath.format(self.awayTeam.getAbrv()), wx.BITMAP_TYPE_PNG).Rescale(50,50).ConvertToBitmap(), name="away")
        self.awayLogo.Bind(wx.EVT_LEFT_DCLICK, self.onClick)
        self.homeLogo = wx.StaticBitmap(homePanel, bitmap= wx.Image(logoPath.format(self.homeTeam.getAbrv()), wx.BITMAP_TYPE_PNG).Rescale(50,50).ConvertToBitmap(), name="home")
        self.homeLogo.Bind(wx.EVT_LEFT_DCLICK, self.onClick)
        
        awaySizer.Add(self.awayLogo, 1)
        awaySizer.Add(self.awayLabel, 0, wx.ALIGN_CENTER)

        homeSizer.Add(self.homeLabel, 0, wx.ALIGN_CENTER)
        homeSizer.Add(self.homeLogo, 1)

        teamsSizer.Add(awayPanel, 1)
        teamsSizer.Add(wx.StaticText(teamsPanel, label=" vs. "), 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 4)
        teamsSizer.Add(homePanel, 1)

        detailsSizer.Add(wx.StaticText(detailsPanel, label="-".join(self.date)), 0)
        detailsSizer.Add(wx.StaticText(detailsPanel, label=self.time), 0)

        mainSizer.Add(teamsPanel, 1, wx.ALIGN_CENTER)
        mainSizer.Add(detailsPanel, 0, wx.ALIGN_CENTER)


    def onClick(self, event):
        name = event.GetEventObject().GetName()
        team = self.awayTeam if name == "away" else self.homeTeam
        print(team.getName())
        self.mainFrame.newTeam(team)



if __name__ == "__main__":

    app = wx.App()

    frame = wx.Frame(None)
    of = SlotPanel(frame, "OF", 3)
    frame.Show()
    app.MainLoop()
        
