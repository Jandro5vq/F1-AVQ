from fastf1Data import *

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

def Check(db, table, GPNum):
    cursor = db.connection.cursor()
    sql = """ SELECT GPNum FROM %s GROUP BY GPNum; """ % (table)
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
        sql = """ INSERT INTO gp (GPID, GPName, GPFormat, GPDate, Cimg, Flagimg, Country, Location, Timezone) 
        VALUES (%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"); """ % (item['RoundNumber'], item['EventName'], item['EventFormat'], item['Session5Date'], item['Cimg'], item['Flagimg'], item['Country'], item['Location'], item['TimeZone'])
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
    if not(Check(db, 'driverpos',  lastGPNum())):
        GPRTable = sorted(ResTable(), key=ResultSorter)
        GPNum = nextGP(y).iloc[0]-1
        cursor = db.connection.cursor()
        for item in GPRTable:
            sql = """ INSERT INTO driverpos (GPNum, DriverID, Pos, Status, Points)
            VALUES (%s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s, "%s", %s) """ % (GPNum, item['Abbreviation'], item['Position'], item['Status'], item['Points'])
            cursor.execute(sql)
        db.connection.commit()

def CreateGPRessTable(db, GPNum): # GP RESULTS BY GP NUMBER TABLE
    if not(Check(db, 'driverpos', GPNum)):
        GPRTable = sorted(ResTable(GPNum), key=ResultSorter)
        cursor = db.connection.cursor()
        for item in GPRTable:
            sql = """ INSERT INTO driverpos (GPNum, DriverID, Pos, Status, Points)
            VALUES (%s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s, "%s", %s) """ % (GPNum, item['Abbreviation'], item['Position'], item['Status'], item['Points'])
            cursor.execute(sql)
        db.connection.commit()

def CreateGPFastLaps(db, GPNum): # GP FAST LAP TIME
    if not(Check(db, 'fastlaptime', GPNum)):
        GPFLTable = sorted(FastLaps(GPNum), key=LapTimeSorter)
        cursor = db.connection.cursor()
        for item in GPFLTable:
            sql = """ INSERT INTO fastlaptime (GPNum, DriverID, LapNum, LapTime)
            VALUES (%s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s, %s) """ % (GPNum, item['Driver'], item['LapNumber'], item['LapTime'])
            cursor.execute(sql)
        db.connection.commit()

def AddBet(db, bet):
    cursor = db.connection.cursor()
    sql = """ SELECT CASE GPID WHEN %s THEN 'True' ELSE 'False' END HasBet
    FROM bets INNER JOIN user ON user.UserID = bets.UserID
    WHERE UserName = '%s' GROUP BY bets.UserID; """ % (bet[0]['GP'], bet[0]['User'])
    cursor.execute(sql)
    db.connection.commit()
    B = cursor.fetchone()
    if B is not None:
        if B[0] == 'True':
            B = True
        else:
            B = False
    else:
        B = False
    if B:
        print("-----> Update")
        for x in range(len(bet) - 1):
            sql = """ UPDATE bets
            SET DriverID = (
                SELECT DriverID
                FROM driver
                WHERE Abv = '%s')
            WHERE UserID = (SELECT UserID FROM user WHERE UserName = "%s") AND GPID = %s AND Pos = %s; """ % (bet[x + 1]['Name'], bet[0]['User'], bet[0]['GP'], bet[x + 1]['pos'])
            cursor.execute(sql)
    else:
        print("-----> Create")
        for x in range(len(bet) - 1):
            sql = """ INSERT INTO bets (UserID, GPID, DriverID, Pos)
            VALUES ((SELECT UserID FROM user WHERE UserName = "%s"), %s, (SELECT DriverID FROM driver WHERE Abv = "%s"), %s) """ % (bet[0]['User'], bet[0]['GP'], bet[x + 1]['Name'], bet[x + 1]['pos'])
            cursor.execute(sql)
    db.connection.commit()