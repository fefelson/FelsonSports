import wx


class PlayerScorePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.teamPlayerBox = wx.ListBox(self)
        self.oppPlayerBox = wx.ListBox(self)

        self.comboBox = wx.ComboBox(self, value="Team", choices=("Team", "Opp"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.comboBox)
        sizer.Add(self.teamPlayerBox)
        sizer.Add(self.oppPlayerBox)

        self.oppPlayerBox.Hide()



        self.SetSizer(sizer)
