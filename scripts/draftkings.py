import csv
import sqlite3
from pprint import pprint
from json import load
from collections import Counter
import datetime

throwsCmd = "SELECT throws FROM pro_players WHERE player_id = ?"
pitchesCmd = "SELECT pitch_type, mph, pct FROM pitch_totals WHERE player_id = ?"
similarPitchCmd = "SELECT pro_players.player_id FROM pro_players INNER JOIN pitch_eval ON pro_players.player_id = pitch_totals.player_id WHERE throws = '{}' AND pitch1 = '{}' AND (mph1 BETWEEN {} AND {}) AND pitch2 = '{}' AND (mph2 BETWEEN {} AND {}) AND k_pitch = {} AND (fly_pct BETWEEN {} AND {}) AND (swing_pct BETWEEN {} AND {}) AND (first_pitch_pct BETWEEN {} AND {})"
teamIdCmd = "SELECT team_id FROM dk_teams WHERE dk_teams.abrv = ?"

cutoff = datetime.date.today() - datetime.timedelta(7)
year, month, day = str(cutoff).split("-")
cutoff = float(month+"."+day)


l30Year, l30Month, l30Day = str(datetime.date.today() - datetime.timedelta(30)).split("-")
last30Date = "{}.{}".format(l30Month, l30Day)
bat30Cmd = "SELECT COUNT(games.game_id), SUM(ab), SUM(bb), SUM(r), SUM(h), SUM(dbl), SUM(tpl), SUM(hr), SUM(rbi), SUM(sb), SUM(so) FROM batting_stats INNER JOIN games ON games.game_id = batting_stats.game_id WHERE player_id = ? AND game_day > ? AND season = ? GROUP BY player_id"
throws30Cmd = "SELECT COUNT(batting_stats.game_id), SUM(ab), SUM(bb), SUM(r), SUM(h), SUM(dbl), SUM(tpl), SUM(hr), SUM(rbi), SUM(sb), SUM(so) FROM batting_stats WHERE batting_stats.player_id = ? AND batting_stats.game_id in (SELECT games.game_id FROM games, positions, pro_players WHERE positions.game_id = games.game_id AND positions.position = 'SP' AND positions.player_id = pro_players.player_id AND pro_players.throws = ? AND game_day > ? AND season = ? ) GROUP BY batting_stats.player_id"
pitch30Cmd = "SELECT COUNT(games.game_id), SUM(w), SUM(ip), SUM(bb), SUM(h), SUM(er), SUM(k) FROM pitching_stats INNER JOIN games ON games.game_id = pitching_stats.game_id WHERE player_id = ? AND game_day > ? AND season = ? GROUP BY player_id"


def similarPitchers(pitcher, curs):
    xpitchers = []
    try:
        cmd = "SELECT first_name, last_name FROM pro_players WHERE player_id = ?"
        curs.execute(cmd,(pitcher[0],))
        first, last = curs.fetchone()
        #print("Pitcher = {} {}".format(first, last))
        
        cmd = "SELECT * FROM pitch_eval WHERE player_id = ?"
        curs.execute(cmd,(pitcher[0],))
        _, throws, pitch1, mph1, pitch2, mph2, kPitch, flyPct, swingPct, firstPitchPct = curs.fetchone()
        #print(throws, pitch1, mph1, pitch2, mph2, kPitch, flyPct, swingPct, firstPitchPct)
        cmd = "SELECT player_id FROM pitch_eval WHERE throws = '{}' AND pitch1 = '{}' AND(mph1 BETWEEN {} AND {}) AND pitch2 = '{}' AND (mph2 BETWEEN {} AND {}) AND k_pitch = '{}'".format(throws, pitch1, mph1  -1, mph1 +1, pitch2, mph2 -1.5, mph2 + 1.5, kPitch)
        #print(cmd)
        curs.execute(cmd)
        xpitchers = [p[0] for p in curs.fetchall() if p[0] != pitcher[0]]

        cmd = "SELECT player_id FROM pitch_eval WHERE throws = '{}' AND (fly_pct BETWEEN {} AND {}) AND (swing_pct BETWEEN {} AND {}) AND (first_pitch_pct BETWEEN {} AND {})".format(throws, flyPct - .02, flyPct + .02, swingPct -.01, swingPct + .01, firstPitchPct - .02, firstPitchPct + .02) 
        curs.execute(cmd)
        for p in curs.fetchall():
            if p[0] != pitcher[0] and p[0] not in xpitchers:
                xpitchers.append(p[0])
    except TypeError:
        pass
    return xpitchers
    

print(cutoff)
mlbDBPath = "/home/ededub/FEFelson/MLB.db"
dkPath = "/home/ededub/FEFelson/Fantasy/Draftkings/MLB/"
scorePath = "/home/ededub/FEFelson/MLB/BoxScores/{}/{}/{}/scoreboard.json"
gamePath = "/home/ededub/FEFelson/MLB/BoxScores/{}/{}/{}/M{}.json"
csvPath = "/home/ededub/Downloads/DKSalaries (61).csv"


conn = sqlite3.connect(mlbDBPath)
curs = conn.cursor()

cmd = "CREATE TEMP TABLE IF NOT EXISTS pitch_eval (player_id TEXT, throws TEXT, pitch1 TEXT, mph1 REAL, pitch2 TEXT, mph2 REAL, k_pitch TEXT, fly_pct REAL, swing_pct REAL, first_pitch_pct REAL)"
curs.execute(cmd)

cmd = "SELECT distinct pitcher_id, throws FROM pitcher_vs_batter INNER JOIN pro_players ON pitcher_vs_batter.pitcher_id = pro_players.player_id ORDER BY player_id"
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

    cmd = "INSERT INTO pitch_eval VALUES (?,?,?,?,?,?,?,?,?,?)"
    curs.execute(cmd,(playerId,throws,pitch1,mph1,pitch2,mph2,so,flypct,swingpct,firstpct))

conn.commit()


players = []
games = []

with open(csvPath) as f:
    f_csv = csv.reader(f)
    for i, row in enumerate(f_csv):
        if i > 0:
            _,_,name,_,pos,price,_,team,_ = row
            players.append((name,pos,price,team))
            games.append(row[6])



for player in players:
    cmd = "SELECT * FROM dk_players WHERE dk_id = ?"
    curs.execute(cmd, (player[0],))
    if not curs.fetchone():
        try:
            first, last = player[0].split()
        except ValueError:
            index = int(input(player[0].split()))
            first = " ".join(player[0].split()[:index])
            last = " ".join(player[0].split()[index:])
        print(first, last)

        cmd = "SELECT player_id FROM pro_players WHERE first_name = ? AND last_name = ?"
        curs.execute(cmd,(first,last))
        try:
            playerId = curs.fetchone()[0]
        except TypeError:
            cmd = "SELECT player_id, first_name, last_name FROM pro_players WHERE first_name = ?"
            curs.execute(cmd, (first,))
            pprint(curs.fetchall())
            cmd = "SELECT player_id, first_name, last_name FROM pro_players WHERE last_name = ?"
            curs.execute(cmd, (last,))
            pprint(curs.fetchall())
            playerId = input(first+" "+last+" ")
            playerId = ""


        
            
        if playerId != "-1" or playerId != "":
            cmd = "INSERT INTO dk_players VALUES(?,?)"
            curs.execute(cmd,(player[0],playerId))
            conn.commit()
            
            

gameIds = []
for game in set(games):
    print(game)
    month,day,year = game.split()[1].split("/")
    teamAbrvs = game.split()[0].split("@")
    cmd = "SELECT team_id FROM dk_teams WHERE abrv = ? OR abrv = ?"
    curs.execute(cmd,teamAbrvs)
    teamIds = [x[0] for x in curs.fetchall()]
    gameTime = game.split()[-2]

    with open(scorePath.format(year,month,day)) as fileIn:
        sb = load(fileIn)
        for matchup in sb["games"]:
            if sorted(teamIds) == sorted([team["team_id"] for team in matchup["teams"]]):
                gameIds.append(matchup["game_id"])


                


month,day,year = games[0].split()[1].split("/")
probables = []
for gameId in gameIds:
    with open(gamePath.format(year, month, day, gameId)) as fileIn:
        bs = load(fileIn)
        #pprint(bs["probables"])
        for p in bs["probables"]:
            probables.append(p["player_id"])



pitchers = []
for pitcher in probables:
    cmd = "SELECT dk_id FROM dk_players WHERE player_id = ?"
    curs.execute(cmd, (pitcher,))
    try:
        dkId = curs.fetchone()[0]
        for player in players:
            if player[0] == dkId:
                pitchers.append((pitcher, dkId, player[2], player[3]))
    except TypeError:
        pass
pprint(pitchers)

batters = []
for player in players:
    if player[1] != "P":
        cmd = "SELECT player_id FROM dk_players WHERE dk_id = ?"
        curs.execute(cmd, (player[0], ))
        try:
            playerId = curs.fetchone()[0]
        except TypeError:
            playerId = -1

        batters.append((playerId, player[0], player[1], player[2], player[3]))



for game in set(games):
    print(game)
    month,day,year = game.split()[1].split("/")
    teamAbrvs = game.split()[0].split("@")

    for team in teamAbrvs:
        opp = teamAbrvs[0] if teamAbrvs[0] != team else teamAbrvs[1]
        print(team,opp)
        pitcher = None
        
        
        for p in pitchers:
            if p[3] == opp:
                against = []
                againstSim = []
                pitcher = p
                cmd = "SELECT first_name, last_name, throws FROM pro_players WHERE player_id = ?" 
                curs.execute(cmd, (pitcher[0],))
                try:
                    pFirst, pLast, throws = curs.fetchone()
                except TypeError:
                    pass
                
                
        
        print("Batters\n")
        for bat in batters:
            cmd = "SELECT SUM(ab) FROM batting_stats, games WHERE player_id = ? AND games.game_id = batting_stats.game_id AND season = 2018 and game_day > ?"
            curs.execute(cmd, (bat[0], cutoff))
            ab = curs.fetchone()[0]
            try:
                if bat[4] == team and bat[0] != -1 and ab > 5:
                    cmd = "SELECT first_name, last_name FROM pro_players WHERE player_id = ?"
                    curs.execute(cmd, (bat[0],))
                    
                    try:
                        print("{} {}   {} {}".format(*curs.fetchone(), bat[2], bat[3]))
                        
                        curs.execute(bat30Cmd, (bat[0], last30Date, l30Year))
                        games, ab, bb, r, h, dbl, tpl, hr, rbi, sb, k = curs.fetchone()
                        pts = h/games*3 + dbl/games*2 + tpl/games*5 + hr/games*7 + rbi/games*2 + r/games*2 + bb/games*2 + sb/games*5
                        print("Last 30  - PTS: {}   Games: {}  AB: {}".format(pts, games, ab))  

                        curs.execute(throws30Cmd, (bat[0], throws, last30Date, l30Year))
                        games, ab, bb, r, h, dbl, tpl, hr, rbi, sb, k = curs.fetchone()
                        pts = h/games*3 + dbl/games*2 + tpl/games*5 + hr/games*7 + rbi/games*2 + r/games*2 + bb/games*2 + sb/games*5
                        print("Throws 30  - PTS: {}   Games: {}  AB: {}".format(pts, games, ab))  
                        
                        #cmd = "SELECT (SUM(h)*1.0) / (SUM(ab)*1.0), (SUM(h) + SUM(dbl) + (SUM(tpl)*2.0) + (SUM(hr)*3.0))/ (SUM(ab)*1.0), SUM(ab), SUM(k) FROM pitcher_vs_batter WHERE pitcher_vs_batter.batter_id = ? AND pitcher_vs_batter.pitcher_id = ?"
                        cmd = "SELECT SUM(ab), (SUM(k)*4.0)/SUM(ab), (SUM(bb) *4.0)/SUM(ab), (SUM(h) *4.0)/SUM(ab), (SUM(dbl)*4.0)/SUM(ab), (SUM(tpl)*4.0)/SUM(ab), (SUM(hr)*4.0)/SUM(ab) FROM pitcher_vs_batter WHERE pitcher_vs_batter.batter_id = ? AND pitcher_vs_batter.pitcher_id = ?"
                        curs.execute(cmd, (bat[0],pitcher[0]))
                        ab,k,bb,h,dbl,tpl,hr = curs.fetchone()
                        cmd = "SELECT (SUM(R)*4.0)/SUM(ab), (SUM(RBI)*4.0)/SUM(ab), (SUM(SB)*4.0)/SUM(ab) FROM batting_stats, positions WHERE positions.game_id = batting_stats.game_id AND batting_stats.player_id = ? AND positions.player_id = ? AND positions.position = 'SP'"
                        curs.execute(cmd, (bat[0],pitcher[0]))
                        r,rbi,sb = curs.fetchone()
                        against.append((k,bb,h,r))
                        pts = h*3 + dbl*2 + tpl*5 + hr*7 + rbi*2 + r*2 + bb*2 + sb*5
                        #print("vs {} {}  - AVG: {}  SLG: {}   AB: {}   K: {}".format(pFirst, pLast, pts[0], pts[1], pts[2], pts[3]))
                        print("vs {} {}  - PTS: {}   AB: {}".format(pFirst, pLast, pts, ab))
                        
                    except TypeError:
                        pass


                    try:
                        simPitch = similarPitchers([pitcher[0]], curs)
                        #cmd = "SELECT (SUM(h)*1.0) / (SUM(ab)*1.0), (SUM(h) + SUM(dbl) + (SUM(tpl)*2.0) + (SUM(hr)*3.0))/ (SUM(ab)*1.0), SUM(ab), SUM(k) FROM pitcher_vs_batter WHERE pitcher_vs_batter.batter_id = ? AND pitcher_vs_batter.pitcher_id in "+str(tuple(similarPitchers([p[0]], curs)))
                        cmd = "SELECT SUM(ab), (SUM(k)*4.0)/SUM(ab), (SUM(bb) *4.0)/SUM(ab), (SUM(h) *4.0)/SUM(ab), (SUM(dbl)*4.0)/SUM(ab), (SUM(tpl)*4.0)/SUM(ab), (SUM(hr)*4.0)/SUM(ab) FROM pitcher_vs_batter WHERE pitcher_vs_batter.batter_id = ? AND pitcher_vs_batter.pitcher_id in "+str(tuple(simPitch))
                        if len(simPitch) == 1:
                            cmd = cmd = "SELECT SUM(ab), (SUM(k)*4.0)/SUM(ab), (SUM(bb) *4.0)/SUM(ab), (SUM(h) *4.0)/SUM(ab), (SUM(dbl)*4.0)/SUM(ab), (SUM(tpl)*4.0)/SUM(ab), (SUM(hr)*4.0)/SUM(ab) FROM pitcher_vs_batter WHERE pitcher_vs_batter.batter_id = ? AND pitcher_vs_batter.pitcher_id =" + simPitch
                        curs.execute(cmd, (bat[0],))
                        ab,k,bb,h,dbl,tpl,hr = curs.fetchone()
                        cmd = "SELECT (SUM(R)*4.0)/SUM(ab), (SUM(RBI)*4.0)/SUM(ab), (SUM(SB)*4.0)/SUM(ab) FROM batting_stats, positions WHERE positions.game_id = batting_stats.game_id AND batting_stats.player_id = ? AND positions.position = 'SP' AND positions.player_id in "+str(tuple(similarPitchers([pitcher[0]], curs)))
                        curs.execute(cmd, (bat[0],))
                        r,rbi,sb = curs.fetchone()
                        againstSim.append((k,bb,h,r))
                        pts = h*3 + dbl*2 + tpl*5 + hr*7 + rbi*2 + r*2 + bb*2 + sb*5
                        #print("vs similar  - AVG: {}  SLG: {}   AB: {}   K: {}\n".format(pts[0], pts[1], pts[2], pts[3]))
                        print("vs similar  - PTS: {}   AB: {}\n".format(pts,ab))
                        
                    except TypeError:
                        print("\n")
                        
            except TypeError:
                pass

        
        
        print("Pitcher")
        try:
            
            print("{} {}  {}   {}\n".format(pFirst, pLast, throws, pitcher[2]))
            curs.execute(pitch30Cmd, (pitcher[0], last30Date, l30Year))
            games, w, ip, bb, h, er, k = curs.fetchone()
            points = w/games*4 + (ip/games*2.25) + (h/games*-.6) + (bb/games*-.6) + (k/games*2.0) + (er/games*-2)
            print("Last 30  - PTS: {}   Games: {}".format(pts, games))
        except TypeError:
            pass
        except NameError:
            pass
        try:
            total = 0.0
            simTotal = 0.0
            for x in against:
                k,bb,h,r = x
                try:
                    total += ((3-h)*.75) + (h*-.6) + (bb*-.6) + (k*2.0) + (r*-2)
                except TypeError:
                    pass
            for x in againstSim:
                k,bb,h,r = x
                try:
                    simTotal += ((3-h)*.75) + (h*-.6) + (bb*-.6) + (k*2.0) + (r*-2)
                except TypeError:
                    pass
            print("vs Team {}".format(total))
            print("vs Similar  {}\n".format(simTotal))
        except TypeError:
            pass

conn.close()
    
