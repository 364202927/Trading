import ccxt,sys,time,os,datetime
from information import information
from util.pdData import pdData
from datetime import timedelta

print("ccxt版本",ccxt.__version__)

# sys.path.append(os.path.abspath("../util"))
# from util.const import const
# k = const._const()

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

tf_Transform = {'1m': '60',
            '3m': '180',
            '5m': '300',
            '15m': '900',
            '30m': '1800',
            '1h': '3600',
            '2h': '7200',
            '4h': '14400',
            '6h': '21600',
            '12h': '43200',
            '1d': '86400',
            '1w': '604800',
            '1M': '2678400',
            '3M': '8035200',
            '6M': '16070400',
            '1y': '31536000'}

class exchange:
    "交易所"
    __ex = None
    __pdData = None
    __informationData = None
    __candles = {'spot':[], 
                'future':[]}
    
    def __init__(self, name):
        # self.__name = name
        self.__informationData = information[name]
        self.__pdData = pdData()
        if self.__informationData == None:
            error(name,"交易所api为空，创建失败")
            return

        exchangeClass = getattr(ccxt, name)
        self.__ex = exchangeClass({
            'apiKey': self.__informationData['apiKey'],
            'secret': self.__informationData['secret'],
            'timeout': 30000,
            'enableRateLimit': True,
        })

    def name(self):
        return self.__ex.id

    def ticker(self):
        # fetchTickers 全部币种行情
        # price = self.__ex.fetch_ticker("BTC/USDT")
        # price = self.__ex.fetchTickers()
        # symbol, timeframe='1m', since=None, limit=None
        # price = self.__ex.fetch_ohlcv("BTC/USDT", '1d',)
        print("~~~~ticker~~~~~", price, self.__ex.markets)

    # def candle(self):
    #     pass

    #todo:时间要检测，end_time<start_time 提醒
    # 获取k线历史：symbolOrTab(一个或多组数据) ，end_time（默认一天）
    def historical_Candle(self, symbolOrTab, start_time, end_time = 1, timeFrameOrTab = "30m", save2File = False):
        # 参数处理        
        start_time += ' 00:00:00'
        end_time = str(self.__pdData.datetime(start_time) + timedelta(days=end_time)) if type(end_time) == int else end_time + ' 00:00:00'
        timeTab = [timeFrameOrTab] if type(timeFrameOrTab) == str else timeFrameOrTab
        symbolTab = [symbolOrTab] if type(symbolOrTab) == str else symbolOrTab
        #交易所全部交易对
        if symbolOrTab == 'all': 
            market = self._sMarkets()
            self.__pdData.format('markets',market)
            symbolTab = self.__pdData.data()
        # 比较最后时间，跳出拉取币种数据
        def compTime(symbol, data):
            def okex(): #ok是反向搜索的
                lastTime = self.__pdData.datetime(data[-1][0],"ms")
                return start_time, lastTime, lastTime <= self.__pdData.datetime(start_time)
            #logic
            funTab = {
                'okex3':okex,
            }
            if funTab.get(self.name()):
                return funTab[self.name()]()
            lastTime = self.__pdData.datetime(data[-1][0],'ms')
            return lastTime, end_time, lastTime >= self.__pdData.datetime(end_time)
        #单币种数据获取
        def symbolData(symbol, timeFrame, fileInfo):
            # print("~~~币种~~~~~",symbol, timeFrame, fileInfo)
            symbolData = self._getSymbolData(symbol, timeFrame, start_time, end_time, self.__informationData['maxLimit'], compTime)
            if len(symbolData) > 0:
                self.__pdData.format("candleConcat", symbolData, start_time, end_time,saveData = fileInfo)
            # print("~~data~~", self.__pdData.data())
            return symbolData
        # 拉取全部交易对
        self._pull(symbolTab, timeTab, start_time, symbolData, save2File and 'spot' or '')

    def fhistorical_Candle(self, symbolOrTab, start_time, end_time = 1, timeFrameOrTab = "5m", save2File = False):
        start_time += ' 00:00:00'
        end_time = str(self.__pdData.datetime(start_time) + timedelta(days=end_time)) if type(end_time) == int else end_time + ' 00:00:00'
        timeTab = [timeFrameOrTab] if type(timeFrameOrTab) == str else timeFrameOrTab
        symbolTab = [symbolOrTab] if type(symbolOrTab) == str else symbolOrTab
        #交易所全部交易对
        if len(symbolOrTab) == 0 and symbolOrTab.endswith('All'): 
            market = self._fMarkets((symbolOrTab == 'bAll' or symbolOrTab == 'sAll') and False) #todo:全币种获取需测试
            self.__pdData.format('markets',market)
            symbolTab = self.__pdData.data()
            print("~~~~all~~~", symbolTab)

        def compTime(symbol, data):
            def okex(): #ok是反向搜索的
                lastTime = self.__pdData.datetime(data[-1][0],"ms")
                return start_time, lastTime, lastTime <= self.__pdData.datetime(start_time)

            def binance():
                if isDapi(symbol):# 币币api数据是反向出数据
                    lastTime = self.__pdData.datetime(data[0][0],'ms',8)
                    return start_time, lastTime, lastTime <= self.__pdData.datetime(start_time)
                lastTime = self.__pdData.datetime(data[-1][0],'ms',8)
                return lastTime, end_time, lastTime >= self.__pdData.datetime(end_time)

            #logic
            funTab = {
                'binance':binance,
                'okex3':okex,
            }
            if funTab.get(self.name()):
                return funTab[self.name()]()

        def symbolData(symbol, timeFrame, fileInfo):
            # print("~~~币种~~~~~",symbol, timeFrame, fileInfo)
            symbolData = self._getSymbolData(symbol, timeFrame, start_time, end_time, self.__informationData['fmaxLimit'], compTime,True)
            if len(symbolData) > 0:
                utcTime = 8 if self.name() == 'binance' else 0
                self.__pdData.format("candleConcat", symbolData, start_time, end_time,saveData = fileInfo, utc = utcTime)
            # print("~~~symbolData~~~",self.__pdData.datetime(symbolData[-1][0],'ms'))
            return symbolData

        # 拉取全部交易对
        self._pull(symbolTab, timeTab, start_time, symbolData, save2File and 'future' or '')


    def updataFetch(self):
        print(self.__ex.fetch_balance())



    #*********todo:后面会从新整理到新文件*************************************************
    def _pull(self, symbolTab:list, timeTab:list, start_time:str, funcSymbolData, saveName:str = ''):
        fileInfo = None
        errorsList = []
        for symbol in symbolTab:
            for timeFrame in timeTab:
                if saveName != '':
                    fileInfo = [self.name(), saveName,start_time[:4]]
                    fileInfo.append(midReplace(symbol)+"_"+timeFrame)
                symbolData = funcSymbolData(symbol, timeFrame, fileInfo)
                if len(symbolData) == 0:
                    errorsList.append(midReplace(symbol)+"_"+timeFrame)  #todo:bug日期还是要的，可能会覆盖掉文件
                    continue
                time.sleep(0.1)
        if len(errorsList) > 0:
            print("~~~~错误列表~~~~", errorsList)

    #获取一只币报价数据
    def _getSymbolData(self, symbol:str, frame:str, beginTime:str, end_time:str, limit:int, compFunc, isFuture = False):
        historyKlineFunc = self._historyKline
        if isFuture:
            historyKlineFunc = self._fhistoryKline
        # print("~~~获取数据~~",symbol, frame)
        allData = []
        while True:
            data = historyKlineFunc(symbol=symbol, timeframe=frame,since = str(beginTime), endTime = str(end_time),  limit=limit)          
            if len(data) == 0:
                return allData
            allData.append(data)
            beginTime, end_time, isOver = compFunc(symbol, data)
            if isOver:
                break;
            time.sleep(0.5)
        return allData

    def _sMarkets(self):
        return self.__ex.load_markets()

    def _fMarkets(self, isDapi = False): #是否币本位
        symbols = []
        def binance():
            if isDapi:  #币本位
                data = self.__ex.dapiPublicGetExchangeInfo()
            else:       #u本位
                data = self.__ex.fapiPublicGetExchangeInfo()
            for pair in data['symbols']:
                symbols.append(pair['symbol'])

        def okex():
            if isDapi:  #永续合约
                data = self.__ex.swapGetInstruments()
            else:       #交割合约
                data = self.__ex.futuresGetInstruments()
            for tab in data:
                symbols.append(tab['instrument_id'])

        # logic
        funTab = {
            'binance':binance,
            'okex3':okex,
        }
        if funTab.get(self.name()):
            funTab[self.name()]()
        return  symbols

    def _historyKline(self, symbol, timeframe, since, endTime, limit):
        def okex():
            params = {
                'instrument_id': midReplace(symbol),
                'granularity': tf_Transform[timeframe],
                'start':time2Iso(endTime),
                'limit':limit}
            try:
                data = self.__ex.spotGetInstrumentsInstrumentIdHistoryCandles(params=params)
                for unit in data:# 转换成时间挫
                    unit[0] = self.__ex.parse8601(iso2Time(unit[0]))
            except:
                data = []
            return data
        # logic
        funTab = {
            'okex3':okex,
        }
        if funTab.get(self.name()):
            return funTab[self.name()]()
        return self.__ex.fetch_ohlcv(symbol = symbol, timeframe = timeframe,since = self.__ex.parse8601(since), limit=limit)

    def _fhistoryKline(self, symbol, timeframe, since, endTime,limit):
        def binance():
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'startTime':date2Time(since),
                'endTime':date2Time(endTime),
                'limit':limit}
            if isDapi(symbol):
                data = self.__ex.dapiPublicGetKlines(params=params)
            else:
                data = self.__ex.fapiPublicGetKlines(params=params)
            return data

        def okex():
            params = {
                'instrument_id': symbol,
                'granularity': tf_Transform[timeframe],
                'start': time2Iso(endTime),
                'limit':limit}
            if isDapi(symbol):
                data = self.__ex.swapGetInstrumentsInstrumentIdHistoryCandles(params=params)
            else:
                data = self.__ex.futuresGetInstrumentsInstrumentIdHistoryCandles(params=params)
            for unit in data:# 转换成时间挫
                unit[0] = self.__ex.parse8601(iso2Time(unit[0]))
            return data
            
        # logic
        funTab = {
            'binance':binance,
            'okex3':okex,
        }
        if funTab.get(self.name()):
            return funTab[self.name()]()