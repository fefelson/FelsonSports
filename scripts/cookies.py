import os
import json
import re
from collections import Counter
from itertools import chain
from operator import itemgetter
from pprint import pprint



pitchTypes = {"1":"Fastball", "2":"Curveball", "3":"Slider", "4":"Changeup",
              "6":"Knuckleball", "7":"Unknown", "8":"Split-Finger", "9":"Cut Fastball",}


resultTypes = {"0":"Ball", "1":"Called Strike", "2":"Swinging Strike", "3":"Foul Ball",
               "5":"Bunt Foul", "10":"In Play",}



def manageText(text):
    text = re.sub("\[.*?\]","player",text)
    text = re.sub("\(.*?\)","",text)
    text = text.split(".")[0]
    text = text.split(",")[0].strip()
    text = "batter reached on hit" if re.search("singled|doubled|tripled|homered|inside the park home run|infield single|ground rule double", text) else text
    text = "batter struck out" if re.search("struck out", text) else text
    text = "player walked" if re.search("walked", text) else text
    text = "player grounded out" if re.search("grounded out", text) else text
    text = "player flied out" if re.search("flied out",text) else text
    text = "player lined out" if re.search("lined out", text) else text
    text = "player popped out" if re.search("popped out", text) else text
    text = "player bunt out" if re.search("bunt out", text) else text
    text = "player out on fielder's choice" if re.search("fielder's choice", text) else text
    text = "player double play" if re.search("double play", text) else text
    text = "player triple play" if re.search("triple play", text) else text
    text = "player fouled out" if re.search("fouled out", text) else text
    text = "player sacrificed" if re.search("sacrifice fly|sacrificed", text) else text
    text = "fielding change" if re.search("player at|player in", text) else text
    text = "pitching change" if re.search("pitching", text) else text
    text = "catching change" if re.search("catching", text) else text
    text = "runner stolen base" if re.search("stole", text) else text
    text = "runner caught stealing" if re.search("caught stealing", text) else text
    text = "batter reached on error" if re.search("fielding error|throwing error", text) else text
    text = "runner advance on pitch" if re.search("player scored|stolen base|player to third|wild pitch|balk|passed ball|fielder's indifference", text) else text
    text = "batter out on pitch" if re.search("out of order|struck out|batter's interference", text) else text
    text = "runner out attempting to advance" if re.search("picked off|out advancing on throw|caught stealing", text) else text
    text = "batter hit into an out" if re.search("grounded out|flied out|lined out|popped out|bunt out|fouled out|sacrificed|fielder's choice|double play|triple play", text) else text
    text = "field change" if re.search("Inning", text) else text
    text = "batter reached non hit" if re.search("hit by pitch|walked|error", text) else text
    return text




pitchCount = Counter()
filePath = os.environ["HOME"] + "/Desktop/Baseball/"
for gamePath in os.listdir(filePath)[:1]:
    #print(gamePath)
    
    #gamePath = "390423302.json"
    gameStats = {}
    with open(filePath+gamePath) as fileIn:
        gameStats = json.load(fileIn)

       
    pbp = gameStats["play_by_play"].values()
    pitches = gameStats["pitches"].values()

    for play in sorted(chain(pbp,), key=lambda x: int(x["play_num"])):
        if int(play.get("ball_hit", 0)):
            pprint(play)
            print("\n\n")
            #pitchCount.update(play["hit_style"].split(","))
##            pprint(play)
##            print("\n\n")
        
    
##    for play in sorted(pbp.values(), key=lambda x: int(x["period"])):
##        pprint(play)
##        print("\n")
##        text = manageText(play["text"])
##        pitchCount.update(text.split(","))
##        #print("\n")
##        try:
##            for pitch in play["pitches_ids"].split(","):
##                pprint(gameStats["pitches"][pitch])
##                print("\n")
##                #pitchCount.update(gameStats["pitches"][pitch]["vertical"].split())
####                if gameStats["pitches"][pitch]["pitch_type"] == "10":
####                    pprint(gameStats["pitches"][pitch])
####                    print(int(int(gameStats["pitches"][pitch]["period"])/2)+1, int(int(gameStats["pitches"][pitch]["period"])%2))
####                    print()
##        except KeyError:
##            pass

    # for each pitch_type in pitchCount
##    for pitchResult in pitchCount.keys():
##        # If pitchCount has a pitch that is not in pitchTypes
##        if pitchResult not in resultTypes.keys():
##            print(pitchResult)
##            input()
##            # print url
##            print(gameStats["game"]["url"])
##            for play in sorted(pbp.values(), key=lambda x: int(x["period"])):
##                try:
##                    for pitch in play["pitches_ids"].split(","):
##                        if gameStats["pitches"][pitch]["result"] == pitchResult:
##                            pprint(gameStats["pitches"][pitch])
##                            print(int(int(gameStats["pitches"][pitch]["period"])/2)+1, int(int(gameStats["pitches"][pitch]["period"])%2))
##                            print()
##                except KeyError:
##                    pass
##            input()

   # print("\n\n")

#pprint(pitchCount)
