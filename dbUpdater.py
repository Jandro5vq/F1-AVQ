from fastf1Data import *
import json
from flask import jsonify

# * ----------------------- UTILS ------------------------
def TeamSorter(item):
    return item['TeamName']

def DriverSorter(item):
    return item['FullName']

def ResultSorter(item):
    return item['Position']

def ScheduleSorter(item):
    return item['RoundNumber']

def LapTimeSorter(item):
    return item['LapTime']

def CleanTable(db, table):
    cursor = db.connection.cursor()
    sql = """ TRUNCATE TABLE %s; """ % (table)
    cursor.execute(sql)
    db.connection.commit()

def Check(db, GPNum):
    cursor = db.connection.cursor()
    sql = """ SELECT GPNum FROM driverpos GROUP BY GPNum; """
    cursor.execute(sql)
    Q = cursor.fetchall()
    NQ = []
    for item in Q:
        NQ.append(item[0])
    if GPNum in NQ:
        return True
    else:
        return False

# * ------------------- MAIN FUCNTIONS -------------------
# ? -------------- TABLE CREATION FUNCTIONS --------------
def createScheduleTable(db): # SCHEDULE TABLE
    CleanTable(db, 'gp')
    STable = sorted(ScheduleTable(), key=ScheduleSorter)
    cursor = db.connection.cursor()
    for item in STable:
        sql = """ INSERT INTO gp (GPID, GPName, GPFormat, GPDate, Cimg, Flagimg) 
        VALUES (%s, "%s", "%s", "%s", "%s", "%s"); """ % (item['RoundNumber'], item['EventName'], item['EventFormat'], item['Session5Date'], item['Cimg'], item['Flagimg'])
        cursor.execute(sql)
    db.connection.commit()

def createTeamTable(db): # TEAM TABLE
    CleanTable(db, 'team')
    TList = sorted(TeamList(), key=TeamSorter)
    cursor = db.connection.cursor()
    for item in TList:
        sql = """ INSERT INTO team (TeamName, TeamColor, img) 
        VALUES ("%s", "%s", "%s"); """ % (item['TeamName'], item['TeamColor'], item['img'])
        cursor.execute(sql)
    db.connection.commit()

def createDriveTable(db): # DRIVER TABLE
    CleanTable(db, 'driver')
    DList = sorted(DriverList(), key=DriverSorter)
    cursor = db.connection.cursor()
    for item in DList:
        sql = """ INSERT INTO driver (TeamID, Abv, DriverName, img) 
        VALUES ((SELECT TeamID FROM team WHERE TeamColor = "%s"), "%s", "%s", "%s"); """ % (item['TeamColor'], item['Abbreviation'], item['FullName'], item['img'])
        cursor.execute(sql)
    db.connection.commit()

def CreateLastGPResTable(db): # LAST GP RESULTS TABLE
    if not(Check(db, lastGPNum())):
        GPRTable = sorted(ResTable(), key=ResultSorter)
        GPNum = nextGP(y).iloc[0]-1
        cursor = db.connection.cursor()
        for item in GPRTable:
            sql = """ INSERT INTO driverpos (GPNum, DriverID, Pos, Status, Points)
            VALUES (%s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s, "%s", %s) """ % (GPNum, item['Abbreviation'], item['Position'], item['Status'], item['Points'])
            cursor.execute(sql)
        db.connection.commit()

def CreateGPRessTable(db, GPNum): # GP RESULTS BY GP NUMBER TABLE
    if not(Check(db, GPNum)):
        GPRTable = sorted(ResTable(GPNum), key=ResultSorter)
        cursor = db.connection.cursor()
        for item in GPRTable:
            sql = """ INSERT INTO driverpos (GPNum, DriverID, Pos, Status, Points)
            VALUES (%s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s, "%s", %s) """ % (GPNum, item['Abbreviation'], item['Position'], item['Status'], item['Points'])
            cursor.execute(sql)
        db.connection.commit()

def CreateGPFastLaps(db, GPNum): # GP FAST LAP TIME
    # if not(Check(db, GPNum)):
        GPFLTable = sorted(FastLaps(GPNum), key=LapTimeSorter)
        cursor = db.connection.cursor()
        for item in GPFLTable:
            sql = """ INSERT INTO fastlaptime (GPNum, DriverID, LapNum, LapTime)
            VALUES (%s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s, "%s") """ % (GPNum, item['Driver'], item['LapNumber'], item['LapTime'])
            cursor.execute(sql)
        db.connection.commit()

# ? --------------- DATA GETTING FUNCTIONS ---------------
def dbDriverList(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Name', DriverName, 'Color', TeamColor, 'img', driver.img )) FROM driver INNER JOIN team ON driver.TeamID = team.TeamID; """
    cursor.execute(sql)
    return json.loads((cursor.fetchone())[0])

def dbGPData(db, GPNum = lastGPNum()):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Name', GPName, 'Format', GPFormat, 'Date', GPDate, 'Circuit', Cimg, 'Flag', Flagimg)) FROM gp WHERE GPID = %s """ % (GPNum)
    cursor.execute(sql)
    return json.loads((cursor.fetchone())[0])

def dbGPRes(db, GPNum = lastGPNum()):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Pos', Pos, 'Abv', Abv, 'Name', DriverName, 'Points', Points,'Status', STATUS, 'Color', TeamColor, 'img', img))
    FROM (
        SELECT Pos, Abv, DriverName, Points, Status, TeamColor, driver.img 
            FROM driverpos
            INNER JOIN driver ON driverpos.DriverID = driver.DriverID
            INNER JOIN team ON driver.TeamID = team.TeamID 
            WHERE GPNum = %s
    ) sub """ % (GPNum)
    cursor.execute(sql)
    Q = cursor.fetchone()
    Q = list(Q)[0]
    return Q

def dbGlobalDriverRes(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Pos', Pos, 'Abv', Abv, 'Name', DriverName, 'Points', Points, 'Color', TeamColor, 'img', img))
    FROM (
        SELECT 
            ROW_NUMBER() OVER (ORDER BY SUM(Points) DESC) Pos, 
            Abv, 
            DriverName, 
            SUM(Points) AS Points, 
            TeamColor, 
            driver.img AS img
        FROM driverpos
        INNER JOIN driver ON driverpos.DriverID = driver.DriverID
        INNER JOIN team ON driver.TeamID = team.TeamID
        GROUP BY DriverName
    ) sub """
    cursor.execute(sql)
    Q = cursor.fetchall()
    Q = list(Q)[0]
    return Q

def dbGlobalTeamRes(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Pos', Pos, 'Name', TeamName, 'Points', Points, 'Color', TeamColor, 'img', img))
    FROM (
        SELECT ROW_NUMBER() OVER (ORDER BY SUM(Points) DESC) Pos, TeamName, SUM(Points) AS Points, TeamColor, team.img AS img 
        FROM driverpos
        INNER JOIN driver ON driverpos.DriverID = driver.DriverID
        INNER JOIN team ON driver.TeamID = team.TeamID
        GROUP BY TeamName
    ) sub """
    cursor.execute(sql)
    Q = cursor.fetchall()
    Q = list(Q)[0]
    return Q

def dbCompletedGP(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('ID', GPID, 'Name', GPName))
    FROM gp
    WHERE GPID IN ( 
        SELECT GPNum FROM driverpos
        GROUP BY GPNum
        ) """
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])

def dbFastLap(db, GPNum):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Abv', Abv, 'Color', TeamColor, 'LapNum',  LapNum, 'LapTime',  LapTime, 'img',  driver.img))
    FROM fastlaptime
    INNER JOIN driver ON driver.DriverID = fastlaptime.DriverID
    INNER JOIN team ON team.TeamID = driver.TeamID
    WHERE GPNum = %s """ % (GPNum)
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])