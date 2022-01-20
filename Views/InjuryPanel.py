import wx
import datetime
from pprint import pprint



class PersonPanel(wx.Panel):

    def __init__(self, parent, injury, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)

        try:
            name = wx.StaticText(self, label=injury[0])
        except:
            name = wx.StaticText(self, label="--")
        name.SetFont(wx.Font(wx.FontInfo(10).Bold()))

        comment = wx.StaticText(self, label=injury[1])
        comment.SetFont(wx.Font(wx.FontInfo(9)))

        date = wx.StaticText(self, label=injury[2])
        date.SetFont(wx.Font(wx.FontInfo(9)))

        sizer.Add(name, 1, wx.EXPAND)
        sizer.Add(comment, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        sizer.Add(date, 1, wx.EXPAND)

        try:
            type = wx.StaticText(self, label=injury[3])
            type.SetFont(wx.Font(wx.FontInfo(9)))
            sizer.Add(type, 1, wx.EXPAND)
        except:
            pass





        self.SetSizer(sizer)





class InjuryPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        mainSizer = wx.BoxSizer()
        self.teamSizers = {}

        for hA in ("away", "home"):

            self.teamSizers[hA] = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.teamSizers[hA], 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(mainSizer)


    def setPanel(self, hA, players):
        # for hA in ("away", "home"):
        #     text = wx.StaticText(self, label=" ".join([game]))

        for player in sorted(players, key=lambda x: datetime.date.fromisoformat(x[2]), reverse=True):
            panel = PersonPanel(self, player)
            self.teamSizers[hA].Add(panel, 0, wx.EXPAND | wx.BOTTOM, 10)
            self.teamSizers[hA].Add(wx.StaticLine(self), 0, wx.EXPAND)
