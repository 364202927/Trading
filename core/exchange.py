import time
from core.baseExchange import baseExchange
from datetime import timedelta
from util.utilities import isDapi,log,midReplace,timeReplace

class exchange(baseExchange):
    "交易所"
    __candles = {'spot':[], 
                'future':[]}
    
    def __init__(self, name):
        super(exchange, self).__init__(name)

    def name(self):
        return self._ex.id

    def pd(self):
        return self._pdData

    def ticker(self):
        # fetchTickers 全部币种行情
        # price = self.__ex.fetch_ticker("BTC/USDT")
        # price = self.__ex.fetchTickers()
        # symbol, timeframe='1m', since=None, limit=None
        # price = self.__ex.fetch_ohlcv("BTC/USDT", '1d',)
        print("~~~~ticker~~~~~", price, self._ex.markets)

    #todo:时间要检测，end_time<start_time 提醒
    # 获取k线历史：symbolOrTab(一个或多组数据) ，end_time（默认一天）
    def historical_Candle(self, symbolOrTab, start_time, end_time = 1, timeFrameOrTab = "30m", save2File = False):
        # 参数处理        
        start_time += ' 00:00:00'
        end_time = str(self._pdData.datetime(start_time) + timedelta(days=end_time)) if type(end_time) == int else end_time + ' 00:00:00'
        timeTab = [timeFrameOrTab] if type(timeFrameOrTab) == str else timeFrameOrTab
        symbolTab = [symbolOrTab] if type(symbolOrTab) == str else symbolOrTab
        #交易所全部交易对
        if symbolOrTab == 'all': 
            market = self.sMarkets()
            self._pdData.format('markets',market)
            symbolTab = self._pdData.data()
        # 比较最后时间，跳出拉取币种数据
        def compTime(symbol, data):
            def okex(): #ok是反向搜索的
                lastTime = self._pdData.datetime(data[-1][0],"ms")
                return start_time, lastTime, lastTime <= self._pdData.datetime(start_time)
            #logic
            funTab = {
                'okex3':okex,
            }
            if funTab.get(self.name()):
                return funTab[self.name()]()
            lastTime = self._pdData.datetime(data[-1][0],'ms')
            return lastTime, end_time, lastTime >= self._pdData.datetime(end_time)
        #单币种数据获取
        def symbolData(symbol, timeFrame, fileInfo):
            # print("~~~币种~~~~~",symbol, timeFrame, fileInfo)
            dataTab = self._getSymbolData(symbol, timeFrame, start_time, end_time, self._informationData['maxLimit'], compTime)
            if len(dataTab) > 0:
                self._pdData.format("candleConcat", dataTab, start_time, end_time,saveData = fileInfo)
            # print("~~data~~", self._pdData.data())
            return dataTab
        # 拉取全部交易对
        self._pull(symbolTab, timeTab, timeReplace(start_time, end_time), symbolData, save2File and 'spot' or '')

    def fhistorical_Candle(self, symbolOrTab, start_time, end_time = 1, timeFrameOrTab = "5m", save2File = False):
        start_time += ' 00:00:00'
        end_time = str(self._pdData.datetime(start_time) + timedelta(days=end_time)) if type(end_time) == int else end_time + ' 00:00:00'
        timeTab = [timeFrameOrTab] if type(timeFrameOrTab) == str else timeFrameOrTab
        symbolTab = [symbolOrTab] if type(symbolOrTab) == str else symbolOrTab
        #交易所全部交易对
        if len(symbolOrTab) == 0 and symbolOrTab.endswith('All'): 
            market = self.fMarkets((symbolOrTab == 'bAll' or symbolOrTab == 'sAll') and False) #todo:全币种获取需测试
            self._pdData.format('markets',market)
            symbolTab = self._pdData.data()
            print("~~~~all~~~", symbolTab)

        def fnCompTime(symbol, data):
            def okex(): #ok是反向搜索的
                lastTime = self._pdData.datetime(data[-1][0],"ms")
                return start_time, lastTime, lastTime <= self._pdData.datetime(start_time)

            def binance():
                if isDapi(symbol):# 币币api数据是反向出数据
                    lastTime = self._pdData.datetime(data[0][0],'ms',8)
                    return start_time, lastTime, lastTime <= self._pdData.datetime(start_time)
                lastTime = self._pdData.datetime(data[-1][0],'ms',8)
                return lastTime, end_time, lastTime >= self._pdData.datetime(end_time)

            #logic
            funTab = {
                'binance':binance,
                'okex3':okex,
            }
            if funTab.get(self.name()):
                return funTab[self.name()]()

        def fnSymbolData(symbol, timeFrame, fileInfo):
            allData = self._getSymbolData(symbol, timeFrame, start_time, end_time, self._informationData['fmaxLimit'], fnCompTime,True)
            if len(allData) > 0:
                utcTime = 8 if self.name() == 'binance' else 0
                self._pdData.format("candleConcat", allData, start_time, end_time, saveData = fileInfo, utc = utcTime)
            return allData
        # 拉取全部交易对
        self._pull(symbolTab, timeTab, timeReplace(start_time, end_time), fnSymbolData, save2File and 'future' or '')

    #全部币的历史数据
    def _pull(self, symbolTab:list, timeTab:list, deadline:str, funcSymbolData, saveName:str = ''):
        fileInfo = None
        errorsList = []
        for symbol in symbolTab:
            for timeFrame in timeTab:
                # 记录到文件
                if saveName != '':
                    fileInfo = [self.name(), saveName]
                    fileInfo.append(midReplace(symbol)+"_"+ deadline + "_" +timeFrame)
                symbolData = funcSymbolData(symbol, timeFrame, fileInfo)
                if len(symbolData) == 0:
                    errorsList.append(midReplace(symbol)+"_"+timeFrame)
                    continue
                time.sleep(0.1)
        if len(errorsList) > 0:
            log("~~~~错误列表~~~~", errorsList)

    #获取一只币报价数据
    def _getSymbolData(self, symbol:str, frame:str, beginTime:str, end_time:str, limit:int, compFunc, isFuture = False):
        historyKlineFunc = self._historyKline
        if isFuture:
            historyKlineFunc = self._fhistoryKline
        log("~~~获取数据~~",symbol, frame)
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

    def updataFetch(self):
        print(self.__ex.fetch_balance())

    def show(self, func_upData = None):
        pass
