import urllib
import bs4
from pprint import pprint
from json import loads
from unicodedata import normalize


for item in ("college-football", ):#"mlb", "mens-college-basketball", "nfl", "college-football" ):

    html = urllib.request.urlopen("http://www.espn.com/{}/scoreboard/_/date/20170305".format(item))
    parser = bs4.BeautifulSoup(html, "lxml")

    for script in parser.select("script"):
        if "window.espn.scoreboardData" in script.text:
            split = script.text.split("= ")[1].split(";window.espn.scoreboardSettings")[0]
            # Create dict from json
            scoreboard = dict(loads(normalize("NFKC", split)))
            #pprint(scoreboard["events"])
            game = scoreboard["events"][0]
            calendar = scoreboard["leagues"][0]["calendar"]
            pprint(calendar)
