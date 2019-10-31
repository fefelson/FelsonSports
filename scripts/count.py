import json
import os
from pprint import pprint

mainPath = "/home/ededub/FEFelson/MLBProjections/Stadiums/"
teamPath = "/home/ededub/FEFelson/MLBProjections/Teams/"

for filePath in [mainPath +fileName for fileName in os.listdir(mainPath)]:
    with open(filePath) as fileIn:
        pprint(json.load(fileIn))

for filePath in [teamPath +fileName for fileName in os.listdir(teamPath)]:
    with open(filePath) as fileIn:
        info = json.load(fileIn)
        info["stadium_id"] = input(info["city"]+" "+info["mascot"])

    with open(filePath, "w") as fileOut:
        json.dump(info,fileOut)
