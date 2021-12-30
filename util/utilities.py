import datetime,time,os
from importlib import import_module

global_lv = 0 #全局打印等级
kErr = 999
kWarn = 888

def log(*args, switch = None, lv = 1, isSaveFile = False):
    if switch == True or global_lv >= lv: #todo:修改为false
        return
    strInfo = 'Log:'
    if lv == kErr:
        strInfo = 'error:'
    elif lv == kWarn:
        strInfo = 'warn:'
    print(strInfo, *args)
    #todo:记录log到文件

def err(*args, switch = None, isSaveFile = False):
    log(*args, switch = switch,lv = kErr, isSaveFile = isSaveFile)
def warn(*args,switch = None, isSaveFile = False):
    log(*args, switch = switch,lv = kWarn, isSaveFile = isSaveFile)

def sendMsg(id, data):
	print("~~~~消息通知~~~~",id,data)

def date2Time(dataTime:str):
    date = datetime.datetime.strptime(dataTime, "%Y-%m-%d %H:%M:%S").timetuple()
    return int(time.mktime(date) * 1000)

def iso2Time(dataTime:str):
    newTime = dataTime[:-5]
    return newTime.replace('T', ' ')

def time2Iso(dataTime:str):
    newTime = dataTime.replace(' ', 'T')
    return newTime + "Z"

def midReplace(symbolName:str):
    return symbolName.replace('/', '-')

def timeReplace(time1:str, time2:str) ->str:
    def replace(time):
        return time.replace('-','')[:8]
    return replace(time1) + "~"+replace(time2)

def isDapi(symbolName:str):
    return (symbolName.endswith('_PERP') or symbolName.endswith('-SWAP'))

def path2File(path, fileType):
    file_list = []
    strLen = len(fileType)
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(fileType):
                file_path = os.path.join(root, filename)
                file_path = os.path.abspath(file_path)
                file_list.append({'name':filename[:-strLen], 'path':file_path})
    return file_list

def require(modPath):
    mod = import_module(modPath)
    className = modPath[modPath.rfind('.') + 1:]
    try:
        obj = getattr(mod, className)
    except AttributeError:
        err("mainLoop为单例对象，请使用mainLoop_ins")
    return obj
