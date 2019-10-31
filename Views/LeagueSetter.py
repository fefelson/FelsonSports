import datetime
import wx
import wx.adv as wxadv

################################################################################
################################################################################





################################################################################
################################################################################


class LeaguePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)




################################################################################
################################################################################


class LeagueSetter(wx.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer()

        self.ctrl = wxadv.CalendarCtrl(self.panel, date=datetime.date.today())

        self.sizer.Add(self.ctrl)
        self.panel.SetSizer(self.sizer)


################################################################################
################################################################################

if __name__ == "__main__":
    app = wx.App()
    frame = LeagueSetter(None)
    frame.Show()
    app.MainLoop()
