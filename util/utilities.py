import datetime

def sendMsg(id, data):
	print("~~~~消息通知~~~~",id,data)

# def date2Time(dataTime):
#     return time.mktime(datetime.datetime.strptime(dataTime, '%Y-%m-%d').timetuple())

# def conversionTime(time):
#     return int(time // 60 * 60)

# def sinceTime(time, limit, timeframes):
#     return time - limit * timeframes * 1000

def date2Time(dataTime:str):
    date = datetime.datetime.strptime(dataTime, "%Y-%m-%d %H:%M:%S").timetuple()
    return int(time.mktime(date)*1000)

def iso2Time(dataTime:str):
    newTime = dataTime[:-5]
    return newTime.replace('T', ' ')

def time2Iso(dataTime:str):
    newTime = dataTime.replace(' ', 'T')
    return newTime + "Z"

def midReplace(symbolName:str):
    return symbolName.replace('/', '-')

def isDapi(symbolName:str):
    return (symbolName.endswith('_PERP') or symbolName.endswith('-SWAP'))