import os
import wx
import MLBProjections.MLBProjections.DB.MLB as MLB


headShotPath = os.environ["HOME"]+"/Desktop/Baseball/Headshots/{}.png"

class BaseballModel:

    def __init__(self):


        self.db = MLB.MLBDatabase()
        self.db.openDB()
        self.playerId = 8180


    def __del__(self):
        self.db.closeDB()


    def getPlayerId(self):
        return self.playerId


    def getName(self):
        return self.db.curs.execute("SELECT first_name, last_name FROM pro_players WHERE player_id = ?",(self.playerId,)).fetchone()
        




class BaseballController:

    def __init__(self):

        self.model = BaseballModel()
        self.view = BaseballFrame(None)

        name = self.model.getName()
        self.view.firstName.SetLabel(name[0])
        self.view.lastName.SetLabel(name[1])
        png =  wx.Image(headShotPath.format(self.model.getPlayerId()), wx.BITMAP_TYPE_ANY).Scale(85,100).ConvertToBitmap()
        self.view.headShot.SetBitmap(png)


        self.view.Show()
        




class BaseballFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainPanel = wx.Panel(self)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(self.mainSizer)

        infoSizer = wx.BoxSizer(wx.HORIZONTAL)
        nameSizer = wx.BoxSizer(wx.VERTICAL)

        self.headShot = wx.StaticBitmap(self.mainPanel, size=(85,100))
        self.firstName = wx.StaticText(self.mainPanel, label="First Name")
        self.lastName = wx.StaticText(self.mainPanel, label="Last Name")

        nameSizer.Add(self.firstName)
        nameSizer.Add(self.lastName)
        infoSizer.Add(self.headShot)
        infoSizer.Add(nameSizer)
        self.mainSizer.Add(infoSizer)





if __name__ == "__main__":

    app = wx.App()
    c = BaseballController()
    app.MainLoop()
