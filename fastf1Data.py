import fastf1
from datetime import date
import numpy as np
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


dnum = [77, 24, 21, 22, 31, 10, 14, 18, 16, 55, 20, 27, 81, 4, 44, 63, 11, 1, 23, 2]

fastf1.Cache.enable_cache('cache')

today,y, gp =date.today(), date.today().year, 1

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def LoadSession(y, gp, type = 'R'): #? FUNCION PARA CARGAR UNA SESION
    global race
    race = fastf1.get_session(y, gp, type)
    race.load()

def nextGP(y): #? INFO DEL SIGUIENTE GP
    ndf = fastf1.get_event_schedule(y)[["RoundNumber", "EventName", "EventFormat", "Session5Date"]]
    
    for x in range(len(ndf)-1):
        deltaDate = to_integer(ndf.iloc[x + 1][3].to_pydatetime().date()) - to_integer(today)
        if deltaDate > 0:
            return ndf.iloc[x + 1]  

def lastGPNum(): #? NUMERO DEL ULTIMO GP
    return nextGP(y).iloc[0]-1

def timeZone(location): #? TIME ZONE DE LA CIUDAD
    tz = TimezoneFinder()
    geolocator = Nominatim(user_agent="AVQF1")
    loc = geolocator.geocode(location)
    return tz.timezone_at(lng=loc.longitude, lat=loc.latitude)

# * ------------------- Genera Lista {GP SCHEDULE} [RoundNumber][EventName][EventFormat][Session5Date] -------------------
def ScheduleTable():
    ndf = fastf1.get_event_schedule(y)[["RoundNumber", "Country", "EventName", "EventFormat", "Session5Date", "Location"]]
    ndf = ndf.transpose().to_dict()
    ndf.pop(0)
    np.stack(ndf)
    keis = list(ndf.keys())
    finalData = []
    for x in range(len(keis)):
        finalData.append(ndf[keis[x]])
        finalData[x]['Session5Date'] = finalData[x]['Session5Date'].to_pydatetime()
        finalData[x]['Cimg'] = finalData[x]['EventName'] + '.png'
        finalData[x]['Flagimg'] = finalData[x]['Country'] + '.png'
        finalData[x]['TimeZone'] = timeZone(finalData[x]['Location'])
    return finalData

# * ------------------- Genera Lista {GPRes} [Position][Abbreviation][Points][Status] -------------------
def ResTable(GP = nextGP(y).iloc[0]-1):
    LoadSession(y, GP)
    ndf = race.results[["Position", "Abbreviation", "Points", "Status"]]
    ndf = ndf.transpose().to_dict()
    np.stack(ndf)
    keis = list(ndf.keys())
    finalData = []
    for x in range(len(keis)):
        finalData.append(ndf[keis[x]])
    return finalData

# * ------------------- Genera Lista {TEAM} [TeamName][TeamColor] -------------------
def TeamList():
    LoadSession(y, nextGP(y).iloc[0]-1)
    ndf = race.results[["TeamName","TeamColor"]]
    ndf = ndf.drop_duplicates().transpose().to_dict()
    np.stack(ndf)
    keis = list(ndf.keys())
    finalData = []
    for x in range(len(keis)):
        finalData.append(ndf[keis[x]])
        finalData[x]['TeamColor'] = "#" + finalData[x]['TeamColor']
        finalData[x]['img'] = finalData[x]['TeamName'] + '.png'
    return finalData

# * ------------------- Genera Lista {DRIVER} [Abbreviation][FullName][TeamColor][img] -------------------
def DriverList():
    LoadSession(y, nextGP(y).iloc[0]-1)
    ndf = race.results[["Abbreviation", "FullName", "TeamColor", "FirstName"]]
    ndf = ndf.transpose().to_dict()
    np.stack(ndf)
    keis = list(ndf.keys())
    finalData = []
    for x in range(len(keis)):
        finalData.append(ndf[keis[x]])
        finalData[x]['TeamColor'] = "#" + finalData[x]['TeamColor']
        finalData[x]['img'] = finalData[x]['Abbreviation'] + '.png'
        finalData[x].pop('FirstName', None)
    return finalData

# * ------------------- Genera Lista {FastLaps} -------------------
def FastLaps(GPNum = nextGP(y).iloc[0]-1):
    LoadSession(y, GPNum)
    finalData = []
    for x in range(len(dnum)):
        laps = race.laps.pick_driver(dnum[x]).pick_fastest()
        lp = laps[['Driver', 'LapNumber', 'LapTime']].transpose().to_dict()
        finalData.append(lp)
        finalData[x]['LapTime'] = finalData[x]['LapTime'].total_seconds() * 1000
        bott = laps[['Driver', 'LapNumber', 'LapTime']].transpose().to_dict()
        finalData.append(bott)
        finalData[x]['LapTime'] = str(finalData[x]['LapTime'].total_seconds())
    return finalData