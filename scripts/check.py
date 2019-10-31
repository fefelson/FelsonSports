from pprint import pprint
from json import load

filePath = "/home/ededub/FEFelson/MLB/BoxScores/2017/04/02/370402129.json"

with open(filePath) as fileIn:
    pprint(dict(load(fileIn)))
