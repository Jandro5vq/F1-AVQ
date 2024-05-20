from fastf1Data import *
import json

# ? --------------- DATA GETTING FUNCTIONS ---------------
def dbDriverList(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Name', DriverName, 'Abv', Abv, 'Color', TeamColor, 'img', driver.img )) FROM driver INNER JOIN team ON driver.TeamID = team.TeamID; """
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
        ORDER BY Points DESC
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
                ORDER BY Points DESC
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
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Abv', Abv,'Name', DriverName, 'Color', TeamColor, 'LapNum',  LapNum, 'LapTime',  LapTime, 'img',  driver.img))
    FROM fastlaptime
    INNER JOIN driver ON driver.DriverID = fastlaptime.DriverID
    INNER JOIN team ON team.TeamID = driver.TeamID
    WHERE GPNum = %s """ % (GPNum)
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])

def dbGetResPerGP(db):
    cursor = db.connection.cursor()
    sql = "SELECT COUNT(GPID) FROM gp"
    cursor.execute(sql)
    Q = cursor.fetchall()
    str1, str2 = "", ""
    for x in range(Q[0][0]):
        str1 = str1 + ", '%s', GP%s" % (x + 1, x + 1)
        str2 = str2 + ",MAX(CASE WHEN GPNum = %s THEN Points END) AS 'GP%s'" % (x + 1, x + 1)
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Abv', Abv, 'Name', DriverName, 'Color', TeamColor %s))
    FROM(
        SELECT Abv, DriverName, TeamColor
        %s
        FROM driverpos
        INNER JOIN driver ON driver.DriverID = driverpos.DriverID
        INNER JOIN team ON team.TeamID = driver.TeamID
        GROUP BY driverpos.driverID
        ORDER BY SUM(Points) DESC
    ) AS sub """ % (str1, str2)
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])

def dbGetTeamResPerGP(db):
    cursor = db.connection.cursor()
    sql = "SELECT COUNT(GPID) FROM gp"
    cursor.execute(sql)
    Q = cursor.fetchall()
    str1, str2 = "", ""
    for x in range(Q[0][0]):
        str1 = str1 + ", '%s', GP%s" % (x + 1, x + 1)
        str2 = str2 + ",SUM(CASE WHEN GPNum = %s THEN Points END) AS 'GP%s'" % (x + 1, x + 1)
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Name', TeamName, 'Color', TeamColor %s))
    FROM(
        SELECT TeamName, TeamColor
        %s
        FROM driverpos
        INNER JOIN driver ON driver.DriverID = driverpos.DriverID
        INNER JOIN team ON team.TeamID = driver.TeamID
        GROUP BY driver.TeamID
        ORDER BY SUM(Points) DESC
    ) AS sub """ % (str1, str2)
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])

def dbGetUserPoints(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Pos', pos, 'Name', UserName, 'Points', UserPoints))
    FROM (
        SELECT ROW_NUMBER() OVER (ORDER BY SUM(UserPoints) DESC) Pos, UserName, UserPoints
        FROM user
        WHERE UserID > 0
    ) AS sub """
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])

def dbGetSchedule(db):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('ID', GPID,'Name', GPName,'Date', GPDate, 'Country', Country, 'Location', Location, 'Timezone', Timezone))
    FROM gp """
    cursor.execute(sql)
    return json.loads(((cursor.fetchall())[0])[0])

def dbGetBet(db, User, GPNum):
    cursor = db.connection.cursor()
    sql = """ SELECT JSON_ARRAYAGG(JSON_OBJECT('Driver', DriverName, 'Abv', Abv, 'Pos', Pos))
    FROM bets
    INNER JOIN user ON user.UserID = bets.UserID
    INNER JOIN driver ON driver.DriverID = bets.DriverID
    WHERE GPID = %s AND UserName = "%s"
    ORDER BY Pos """ % (GPNum, User)
    cursor.execute(sql)
    B = (cursor.fetchall())[0][0]
    if B is None:
        return []
    else:
        return json.loads(B)
