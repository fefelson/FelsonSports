import sqlite3
from pprint import pprint
from datetime import date
from os import listdir
from json import load
from collections import Counter

mlbDBPath = "/home/ededub/FEFelson/MLB.db"
gamePath = "/home/ededub/FEFelson/MLB/BoxScores/{}/{}/{}/"

today = date.today()

conn = sqlite3.connect(mlbDBPath)
curs = conn.cursor()

probables = []
for fileName in listdir(gamePath.format(*str(today).split("-"))):
    if fileName[0] == "M":
        with open(gamePath.format(*str(today).split("-")) + fileName) as fileIn:
            bs = load(fileIn)
            #pprint(bs["probables"])
            for p in bs["probables"]:
                probables.append(p["player_id"])

cmd = "CREATE TEMP TABLE pitch_eval (player_id TEXT, throws TEXT, pitch1 TEXT, mph1 REAL, pitch2 TEXT, mph2 REAL, k_pitch TEXT, fly_pct REAL, swing_pct REAL, first_pitch_pct REAL)"
curs.execute(cmd)

cmd = "SELECT distinct pitching_stats.player_id, throws FROM pitching_stats INNER JOIN pro_players ON pitching_stats.player_id = pro_players.player_id"
curs.execute(cmd)
for playerId, throws in curs.fetchall():
    #print(playerId, throws)
    cmd = "SELECT MAX(pitch_total), pitch_type FROM (SELECT pitch_type, COUNT(pitch_type) as pitch_total FROM pitch_count WHERE player_id = ? AND result = 'Strike Out' GROUP BY pitch_type)"
    curs.execute(cmd, (playerId,))
    so = curs.fetchone()[1]
    #print(so)
    cmd = "SELECT MAX(pitch_total), pitch_type, mph FROM (SELECT pitch_type, COUNT(pitch_type) as pitch_total, AVG(mph) as mph FROM pitch_count WHERE player_id = ? GROUP BY pitch_type)"
    curs.execute(cmd,(playerId,))
    _,pitch1, mph1 = curs.fetchone()
    #print(pitch1, mph1)
    cmd = "SELECT MAX(pitch_total), pitch_type, mph FROM (SELECT pitch_type, COUNT(pitch_type) as pitch_total, AVG(mph) as mph FROM pitch_count WHERE player_id = ? and pitch_type != ? GROUP BY pitch_type)"
    curs.execute(cmd,(playerId, pitch1))
    _,pitch2, mph2 = curs.fetchone()
    #print(pitch2, mph2)            
    cmd = "SELECT (SUM(fly_ball)/(SUM(fly_ball)+SUM(ground_ball)*1.0)), (SUM(swing_strike)/(SUM(pc)*1.0)), (SUM(first_pitch_strike)/(SUM(batters_faced)*1.0)) FROM pitching_stats WHERE player_id = ?"
    curs.execute(cmd, (playerId,))
    flypct, swingpct, firstpct = curs.fetchone()
    #print(flypct, swingpct, firstpct)
    #print(pitch1,mph1,pitch2,mph2,so,flypct,swingpct,firstpct)
    #print("\n\n\n")
##    if throws == "N/A":
##        cmd = "SELECT first_name, last_name from pro_players WHERE player_id = ?"
##        curs.execute(cmd,(playerId,))
##        print(curs.fetchone())

    cmd = "INSERT INTO pitch_eval VALUES (?,?,?,?,?,?,?,?,?,?)"
    curs.execute(cmd,(playerId,throws,pitch1,mph1,pitch2,mph2,so,flypct,swingpct,firstpct))

conn.commit()

for pitcher in probables:
    #print(pitcher)

##    cmd = "SELECT first_name, last_name, throws FROM pro_players WHERE player_id = ?"
##    curs.execute(cmd,(pitcher,))
##    first, last, throws = curs.fetchone()
##    print(first, last, throws)
##
##    cmd = "SELECT first_name, last_name, throws, pitch_type, mph, pitches*1.0/ total*1.0 as pct FROM pro_players, (SELECT pitch_type, COUNT(pitch_type) as pitches, AVG(mph) as mph FROM pitch_count WHERE player_id = ? GROUP BY pitch_type), (SELECT COUNT(player_id) as total FROM pitch_count  WHERE player_id = ? ) WHERE player_id = ? AND pitch_type not in ('Pitch Out', '--') GROUP BY pitch_type HAVING pct >= .1"
##    curs.execute(cmd, (pitcher,pitcher, pitcher))
##    pprint(curs.fetchall())
##
##    cmd = "DROP VIEW pitch_totals"
##    curs.execute(cmd)
##        
##    cmd = "SELECT pc.player_id, pitch_type, mph, pitches*1.0/ total*1.0 as pct FROM (SELECT player_id, pitch_type, COUNT(pitch_type) as pitches, AVG(mph) as mph FROM pitch_count GROUP BY pitch_type) as pc INNER JOIN (SELECT player_id, COUNT(player_id) as total FROM pitch_count) as pt on pt.player_id = pc.player_id WHERE pitch_type not in ('Pitch Out', '--') GROUP BY pitch_type HAVING pct >= .1"
##    cmd = "SELECT player_id, pitch_type, COUNT(pitch_type) as p_total, AVG(mph) as mph FROM pitch_count GROUP BY player_id, pitch_type"
##    cmd = "CREATE VIEW pitch_totals AS SELECT pc.player_id, pitch_type, mph, p_total*1.0/c_total*1.0 as pct FROM (SELECT player_id, COUNT(player_id) as c_total FROM pitch_count GROUP BY player_id) as pt INNER JOIN (SELECT player_id, pitch_type, COUNT(pitch_type) as p_total, AVG(mph) as mph FROM pitch_count GROUP BY player_id, pitch_type) as pc on pt.player_id = pc.player_id WHERE pitch_type not in ('Pitch Out', '--') AND pct >= .1" 
##    curs.execute(cmd)
##    conn.commit()
##    cmd = "SELECT * FROM pitch_totals WHERE player_id = ?"
##    curs.execute(cmd,(pitcher,))
##    pitches = curs.fetchall()
##    nP = Counter()
##    for pitch in pitches:
##        cmd = "SELECT pro_players.player_id FROM pro_players INNER JOIN pitch_totals ON pro_players.player_id = pitch_totals.player_id WHERE throws = '{}' AND pitch_type = '{}' AND (mph BETWEEN {} AND {}) AND (pct BETWEEN {} AND {})".format(throws, pitch[1], pitch[2]-3, pitch[2]+3, pitch[3]-.05, pitch[3]+.05)
##        curs.execute(cmd)
##        nP.update([x[0] for x in curs.fetchall()])
##
##
##    nP = [x[0] for x in nP.most_common(10) if x[1] >= 2]
##
##    for p in nP:
##        cmd = "SELECT first_name, last_name FROM pro_players WHERE player_id = ?"
##        curs.execute(cmd,(p,))
##        print("")
##        print(curs.fetchone())
##    print("\n\n")

    try:
        cmd = "SELECT first_name, last_name FROM pro_players WHERE player_id = ?"
        curs.execute(cmd,(pitcher,))
        first, last = curs.fetchone()
        print("Pitcher = {} {}".format(first, last))
        
        cmd = "SELECT * FROM pitch_eval WHERE player_id = ?"
        curs.execute(cmd,(pitcher,))
        _, throws, pitch1, mph1, pitch2, mph2, kPitch, flyPct, swingPct, firstPitchPct = curs.fetchone()
        print(throws, pitch1, mph1, pitch2, mph2, kPitch, flyPct, swingPct, firstPitchPct)
        cmd = "SELECT player_id FROM pitch_eval WHERE throws = '{}' AND pitch1 = '{}' AND(mph1 BETWEEN {} AND {}) AND pitch2 = '{}' AND (mph2 BETWEEN {} AND {}) AND k_pitch = '{}'".format(throws, pitch1, mph1  -1, mph1 +1, pitch2, mph2 -1.5, mph2 + 1.5, kPitch)
        #print(cmd)
        curs.execute(cmd)
        pitchers = [p[0] for p in curs.fetchall() if p[0] != pitcher]

        cmd = "SELECT player_id FROM pitch_eval WHERE throws = '{}' AND (fly_pct BETWEEN {} AND {}) AND (swing_pct BETWEEN {} AND {}) AND (first_pitch_pct BETWEEN {} AND {})".format(throws, flyPct - .02, flyPct + .02, swingPct -.01, swingPct + .01, firstPitchPct - .02, firstPitchPct + .02) 
        curs.execute(cmd)
        for p in curs.fetchall():
            if p[0] != pitcher and p[0] not in pitchers:
                pitchers.append(p[0])
        print("\nSimilar Pitchers\n")
        for p in pitchers:
            cmd = "SELECT first_name, last_name FROM pro_players WHERE player_id = ?"
            curs.execute(cmd,(p,))
            first, last = curs.fetchone()
            print("{} {}".format(first,last))
            cmd = "SELECT * FROM pitch_eval WHERE player_id = ?"
            curs.execute(cmd,(p,))
            _, throws, pitch1, mph1, pitch2, mph2, kPitch, flyPct, swingPct, firstPitchPct = curs.fetchone()
            print(throws, pitch1, mph1, pitch2, mph2, kPitch, flyPct, swingPct, firstPitchPct)
            print("\n")
        print("\n\n\n")
    except TypeError:
        pass
    

conn.close()
