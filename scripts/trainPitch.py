from os import environ
from json import load, dump
from datetime import date, timedelta
from itertools import chain
import sqlite3

from sklearn.linear_model import LogisticRegression as LogReg
from sklearn.linear_model import LinearRegression as LinReg

import MLBProjections.MLBProjections.DB.MLB as DB

from pprint import pprint

pitcherValues = ("pitch_num",
                 "batt_order",
                 "turn",
                 "sequence",
                 "pitch_type_id",
                 "pitch_result_id",
                 "velocity",
                 "x_value",
                 "y_value",
                 "side",
                 "balls",
                 "strikes"
                 )

contactValues = ("hit_style",
                 "hit_hardness",
                 "hit_angle",
                 "hit_distance",
                 "pitch_type_id",
                 "pitch_result_id",
                 "velocity",
                 "x_value",
                 "y_value",
                 "turn",
                 "side",
                 "balls",
                 "strikes"
                )

pitchBatValues = ("game_id",
                  "play_num",
                  "pitch_num",
                  "score_diff"
                  )

removeValues = ("game_id",
                "pitcher_id",
                "play_num",
                "pitch_num",
                "score_diff"
                )

replaceValues = ("pitcher_id",
                 "score_diff",
                 "inning"
                 )





def addPlayer(playerId, mlbDB, gameDB):
    playerInfo = mlbDB.curs.execute("SELECT * FROM pro_players WHERE player_id = ?",(playerId,)).fetchone()
    try:
        gameDB.insert(DB.proPlayersTable, playerInfo)
    except sqlite3.IntegrityError:
        pass


def newPitcher(mlbDB, gameDB, teamId, pitcherId, starter=0):
    if not gameDB.curs.execute("SELECT player_id FROM pro_players WHERE player_id = ?",(pitcherId,)).fetchone(): 
        addPlayer(pitcherId, mlbDB, gameDB)
        pitches = None

        try:
            gameDB.insert(DB.bullpenTable, (teamId, pitcherId, starter))
        except sqlite3.IntegrityError:
            pass

        pitchCount = mlbDB.curs.execute("SELECT COUNT(pitcher_id) FROM pitches INNER JOIN pro_players ON pitches.pitcher_id = pro_players.player_id WHERE pitcher_id = ?", (pitcherId,)).fetchone()[0]
        if pitchCount > 200:
            pitches = [dict(zip(pitcherValues,pitch)) for pitch in mlbDB.curs.execute(pitcherCmd, (pitcherId,)).fetchall()]
        else:
            pitches = [dict(zip(pitcherValues,pitch)) for pitch in mlbDB.curs.execute(unknownPitcherCmd, (pitcherId,)).fetchall()][:500]
            print(len(pitches))
        pitchTypes = setPitchTypes(pitcherId, pitches)
        for pitchType in pitchTypes:
            gameDB.insert(DB.pitchTypeLogTables, [pitcherId, "career", int(pitchType[0]), pitchType[1], *pitchType[2]])

        
        pitchVelocity = setPitchVelocity(pitches)
        gameDB.insert(DB.pitchSpeedLinTables, [pitcherId, "career", pitchVelocity[0], *pitchVelocity[1]])

        
        pitchXValue = setPitchX(pitches)
        for xValue in pitchXValue:
            gameDB.insert(DB.pitchXValueLogTables, [pitcherId, "career", int(xValue[0]), xValue[1], *xValue[2]])

        
        pitchYValue = setPitchY(pitches)
        for yValue in pitchYValue:
            gameDB.insert(DB.pitchYValueLogTables, [pitcherId, "career", int(yValue[0]), yValue[1], *yValue[2]])

        pitchResult = setPitchResult(pitches)
        for result in pitchResult:
            gameDB.insert(DB.pitchResultLogTables, [pitcherId, "career", int(result[0]), result[1], *result[2]])

        contacts = [dict(zip(contactValues,contact)) for contact in mlbDB.curs.execute(contactCmd.format({"playerType":"pitcher"}), (pitcherId,)).fetchall()]

        
        contactStyle = setContactStyle(contacts)
        for style in contactStyle:
            gameDB.insert(DB.contactStyleLogTables, [pitcherId, "career", int(style[0]), style[1], *style[2]])

        contactHardness = setContactHardness(contacts)
        for hardness in contactHardness:
            gameDB.insert(DB.contactHardLogTables, [pitcherId, "career", int(hardness[0]), hardness[1], *hardness[2]])
        
        contactAngle = setContactAngle(contacts)
        gameDB.insert(DB.contactAngleLinTables, [pitcherId, "career", contactAngle[0], *contactAngle[1]])

        atbats = [dict(zip(pitchBatValues,atbat)) for atbat in mlbDB.curs.execute(pitcherABCmd, (pitcherId,)).fetchall()]
        removals = [dict(zip(removeValues,remove)) for remove in mlbDB.curs.execute(removeCmd, (pitcherId,)).fetchall()]
        replacements = [dict(zip(replaceValues,replace)) for replace in mlbDB.curs.execute(replaceCmd, (teamId,)).fetchall()]
        
        pitchRemove = setPitchRemove(atbats, removals)
        for remove in pitchRemove:
            gameDB.insert(DB.removePitcherLogTables, [pitcherId, "career", int(remove[0]), remove[1], *remove[2]])


        pitchReplace = setPitchReplace(pitcherId, replacements)
        if pitchReplace:
            for replace in pitchReplace:
                gameDB.insert(DB.replacePitcherLogTables, [pitcherId, "career", int(replace[0]), replace[1], *replace[2]])


def setPitchTypes(playerId, pitches):
    logReg = LogReg(solver="sag", multi_class="multinomial", max_iter=1000)
    X = []
    y = []
    for pitch in pitches:
        keys = DB.pitchTypeLogTables["tableCols"]
        values = [pitch[index] for index in keys[4:]]

        X.append(values)
        y.append(pitch["pitch_type_id"])
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))
        

def setPitchVelocity(pitches):
    linReg = LinReg()
    X = []
    y = []
    for pitch in pitches:
        keys = DB.pitchSpeedLinTables["tableCols"]
        values = [pitch[index] for index in keys[3:]]

        X.append(values)
        y.append(pitch["velocity"])
    linReg.fit(X,y)
    
    return list((linReg.intercept_, linReg.coef_))


def setPitchX(pitches):
    logReg = LogReg(solver="sag", multi_class="multinomial", max_iter=1500)
    X = []
    y = []
    for pitch in [pitch for pitch in pitches if pitch["x_value"] != -1]:
        keys = DB.pitchXValueLogTables["tableCols"]
        values = [pitch[index] for index in keys[4:]]

        X.append(values)
        y.append(pitch["x_value"])
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))



def setPitchY(pitches):
    logReg = LogReg(solver="sag", multi_class="multinomial", max_iter=1500)
    X = []
    y = []
    for pitch in [pitch for pitch in pitches if pitch["y_value"] != -1]:
        keys = DB.pitchYValueLogTables["tableCols"]
        values = [pitch[index] for index in keys[4:]]

        X.append(values)
        y.append(pitch["y_value"])
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))


def setPitchResult(pitches):
    logReg = LogReg(solver="sag", multi_class="multinomial", max_iter=1500)
    X = []
    y = []
    for pitch in [pitch for pitch in pitches if pitch["y_value"] != -1 and pitch["x_value"] != -1]:
        keys = DB.pitchResultLogTables["tableCols"]
        values = [pitch[index] for index in keys[4:]]

        X.append(values)
        y.append(pitch["pitch_result_id"])
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))



def setContactStyle(contacts):
    logReg = LogReg(solver="sag", multi_class="multinomial", max_iter=1000)
    X = []
    y = []
    for contact in [pitch for pitch in contacts if pitch["y_value"] != -1 and pitch["x_value"] != -1]:
        keys = DB.contactStyleLogTables["tableCols"]
        values = [contact[index] for index in keys[4:]]
        
        X.append(values)
        y.append(contact["hit_style"])
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))


def setContactHardness(contacts):
    logReg = LogReg(solver="sag", multi_class="multinomial", max_iter=1500)
    X = []
    y = []
    for contact in [pitch for pitch in contacts if pitch["y_value"] != -1 and pitch["x_value"] != -1]:
        keys = DB.contactHardLogTables["tableCols"]
        values = [contact[index] for index in keys[4:]]
        
        X.append(values)
        y.append(contact["hit_hardness"])
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))


def setContactAngle(contacts):
    linReg = LinReg()
    X = []
    y = []
    for contact in [pitch for pitch in contacts if pitch["y_value"] != -1 and pitch["x_value"] != -1]:
        keys = DB.contactAngleLinTables["tableCols"]
        values = [contact[index] for index in keys[3:]]

        X.append(values)
        y.append(contact["hit_angle"])
    linReg.fit(X,y)
    
    return list((linReg.intercept_, linReg.coef_))


def setPitchRemove(atbats, removals):
    logReg = LogReg(solver="sag", multi_class="ovr", max_iter=1500)
    X = []
    y = []
    
    for play in sorted(chain(atbats,removals), key= lambda x: (int(x["game_id"]),int(x["play_num"]))):
        keys = DB.removePitcherLogTables["tableCols"]
        values = [play[index] for index in keys[4:]]
        result = 1 if play.get("pitcher_id", None) else 0

        X.append(values)
        y.append(result)
    logReg.fit(X,y)
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))


def setPitchReplace(pitcherId, replaces):
    logReg = LogReg(solver="sag", multi_class="ovr", max_iter=1500)
    X = []
    y = []
    for play in replaces:
        
        keys = DB.replacePitcherLogTables["tableCols"]
        values = [play[index] for index in keys[4:]]
        X.append(values)
        y.append(int(int(pitcherId)==int(play["pitcher_id"])))
    try:
        logReg.fit(X,y)
    except ValueError:
        return None
    return list(zip(logReg.classes_, logReg.intercept_, logReg.coef_))




pitcherCmd =  """
                SELECT pitch_num,
                        batt_order,
                        turn,
                        sequence,
                        pitch_type_id,
                        pitch_result_id,
                        velocity,
                        x_value,
                        y_value,
                        (CASE WHEN pitcher.throws = batter.bats THEN 1 ELSE 0 END),
                        balls,
                        strikes 
                FROM pitches
                INNER JOIN pro_players AS pitcher ON pitches.pitcher_id = pitcher.player_id
                INNER JOIN pro_players AS batter ON pitches.batter_id = batter.player_id
                INNER JOIN pitch_locations ON pitches.location_id = pitch_locations.location_id
                INNER JOIN lineups ON pitches.game_id = lineups.game_id AND pitches.batter_id = lineups.player_id 

                WHERE pitcher_id = ?
                """


pitcherABCmd =  """
                SELECT ab_results.game_id,
                        ab_results.play_num,
                        pitch_num,
                        score_diff
                FROM ab_results        
                INNER JOIN pitches ON ab_results.pitch_id = pitches.pitch_id
                WHERE pitcher_id = ?
                """

removeCmd =  """
                SELECT game_id,
                        pitcher_id,
                        play_num,
                        pitch_num,
                        score_diff
                FROM removals        
                WHERE pitcher_id = ?
                """


replaceCmd =  """
                SELECT pitcher_id,
                        score_diff,
                        inning
                FROM new_pitchers        
                WHERE team_id = ?
                """


unknownPitcherCmd =  """
                SELECT pitch_num,
                        batt_order,
                        turn,
                        sequence,
                        pitch_type_id,
                        pitch_result_id,
                        velocity,
                        x_value,
                        y_value,
                        (CASE WHEN pitcher.throws = batter.bats THEN 1 ELSE 0 END),
                        balls,
                        strikes 
                FROM pitches
                INNER JOIN pro_players AS pitcher ON pitches.pitcher_id = pitcher.player_id
                INNER JOIN pro_players AS batter ON pitches.batter_id = batter.player_id
                INNER JOIN pitch_locations ON pitches.location_id = pitch_locations.location_id
                INNER JOIN lineups ON pitches.game_id = lineups.game_id AND pitches.batter_id = lineups.player_id 

                WHERE pitcher_id IN (SELECT other.player_id FROM pro_players AS pp INNER JOIN pro_players AS other ON pp.pos = other.pos AND pp.throws = other.throws WHERE pp.player_id = ?) 
                ORDER BY pitches.pitch_id DESC
                """


contactCmd = """
                    SELECT hit_style,
                            hit_hardness,
                            hit_angle,
                            hit_distance,
                            pitch_type_id,
                            pitch_result_id,
                            velocity,
                            x_value,
                            y_value,
                            turn,
                            (CASE WHEN pitcher.throws = batter.bats THEN 1 ELSE 0 END),
                            balls,
                            strikes
                    FROM contacts
                    INNER JOIN pitches ON contacts.pitch_id = pitches.pitch_id
                    INNER JOIN pro_players AS pitcher ON pitches.pitcher_id = pitcher.player_id
                    INNER JOIN pro_players AS batter ON pitches.batter_id = batter.player_id
                    INNER JOIN pitch_locations ON pitches.location_id = pitch_locations.location_id

                    WHERE {0[playerType]}_id = ?
                    """





matchupPath = environ["HOME"] +"/FEFelson/MLBProjections/Lineups/{}.json"
gameDate = date.today()



mlbDB = DB.MLBDatabase()
mlbDB.openDB()




filePath = matchupPath.format("".join(str(gameDate).split("-")))
with open(filePath) as fileIn:
    info = load(fileIn)


for matchup in info["matchups"]:

    

    
    pprint(matchup)
        
    gameId = matchup["gameId"]
    homeId = matchup["homeTeam"]["teamId"]
    awayId = matchup["awayTeam"]["teamId"]
    stadiumId = mlbDB.curs.execute("SELECT stadium_id FROM pro_teams WHERE team_id = ?", (homeId,)).fetchone()[0]


    gameDB = DB.MLBGame(gameId)
    gameDB.openDB()

    try:
        gameDB.insert(DB.metaTable, (gameId, homeId, awayId, stadiumId))
    except sqlite3.IntegrityError:
        continue


    stadiumInfo = mlbDB.curs.execute("SELECT * FROM stadiums WHERE stadium_id = ?",(stadiumId,)).fetchone()
    stadiumData = mlbDB.curs.execute("SELECT hit_style, hit_hardness, hit_angle, hit_distance, result_type_id FROM contacts INNER JOIN ab_results ON contacts.contact_id = ab_results.contact_id WHERE stadium_id = ? AND hit_style != -1", (stadiumId,)).fetchall()
    for data in stadiumData:
        cabId = gameDB.nextKey({"pk":"c_a_b_id", "tableName": DB.contactAtBatsTable["tableName"]})
        try:
            gameDB.insert(DB.contactAtBatsTable, [cabId,]+list(data))
        except sqlite3.IntegrityError:
            pass
            
        
    
    try:
        gameDB.insert(DB.stadiumsTable, stadiumInfo)
    except sqlite3.IntegrityError:
        pass


    for teamId in (homeId, awayId):
        teamInfo = mlbDB.curs.execute("SELECT * FROM pro_teams WHERE team_id = ?", (teamId,)).fetchone()
        try:
            gameDB.insert(DB.proTeamsTable, teamInfo)
        except sqlite3.IntegrityError:
            pass



    for key in ("homeTeam", "awayTeam"):
        team = matchup[key]

        print(team["starter"])
        starterId = team["starter"][0]

        newPitcher(mlbDB, gameDB, team["teamId"], starterId, True)

        for pitcher in team["bullpen"]:
            print(pitcher)
            pitcherId = pitcher[0]
            newPitcher(mlbDB, gameDB, team["teamId"], pitcherId)
        

       
            

        gameDB.commit()
        mlbDB.closeDB()
        gameDB.closeDB()
        raise AssertionError

      
        
        


    mlbDB.closeDB()
