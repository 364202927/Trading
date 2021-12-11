import ccxt,time
from information import information
from util.pdData import pdData
from util.utilities import iso2Time,date2Time,time2Iso,midReplace,isDapi

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

print("ccxt版本:",ccxt.__version__)
class baseExchange:
	'交易所基类'
	_ex = None
	_pdData = None
	_informationData = None

	def __init__(self, name):
		self._informationData = information[name]
		self._pdData = pdData()
		if self._informationData == None:
			error(name,"交易所api为空，创建失败")
			return

		exchangeClass = getattr(ccxt, name)
		self._ex = exchangeClass({
			'apiKey': self._informationData['apiKey'],
			'secret': self._informationData['secret'],
			'timeout': 30000,
			'enableRateLimit': True,
		})

    #全部币的历史数据
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

	#检测市场全数据
	def _sMarkets(self):
		return self._ex.load_markets()
	def _fMarkets(self, isDapi = False):
		symbols = []
		def binance():
			if isDapi:  #币本位
				data = self._ex.dapiPublicGetExchangeInfo()
			else:       #u本位
				data = self._ex.fapiPublicGetExchangeInfo()
			for pair in data['symbols']:
				symbols.append(pair['symbol'])

		def okex():
			if isDapi:  #永续合约
				data = self._ex.swapGetInstruments()
			else:       #交割合约
				data = self._ex.futuresGetInstruments()
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

	# 现货历史数据
	def _historyKline(self, symbol, timeframe, since, endTime, limit):
		def okex():
			params = {
				'instrument_id': midReplace(symbol),
				'granularity': tf_Transform[timeframe],
				'start':time2Iso(endTime),
				'limit':limit}
			try:
				data = self._ex.spotGetInstrumentsInstrumentIdHistoryCandles(params=params)
				for unit in data:# 转换成时间挫
					unit[0] = self._ex.parse8601(iso2Time(unit[0]))
			except:
				data = []
			return data
        # logic
		funTab = {
			'okex3':okex,
		}
		if funTab.get(self.name()):
			return funTab[self.name()]()
		return self._ex.fetch_ohlcv(symbol = symbol, timeframe = timeframe,since = self._ex.parse8601(since), limit=limit)

	#合约历史数据
	def _fhistoryKline(self, symbol, timeframe, since, endTime,limit):
		def binance():
			params = {
				'symbol': symbol,
				'interval': timeframe,
				'startTime':date2Time(since),
				'endTime':date2Time(endTime),
				'limit':limit}
			if isDapi(symbol):
				data = self._ex.dapiPublicGetKlines(params=params)
			else:
				data = self._ex.fapiPublicGetKlines(params=params)
			return data

		def okex():
			params = {
				'instrument_id': symbol,
				'granularity': tf_Transform[timeframe],
				'start': time2Iso(endTime),
				'limit':limit}
			if isDapi(symbol):
				data = self._ex.swapGetInstrumentsInstrumentIdHistoryCandles(params=params)
			else:
				data = self._ex.futuresGetInstrumentsInstrumentIdHistoryCandles(params=params)
			for unit in data:# 转换成时间挫
				unit[0] = self._ex.parse8601(iso2Time(unit[0]))
			return data
        # logic
		funTab = {
			'binance':binance,
			'okex3':okex,
		}
		if funTab.get(self.name()):
			return funTab[self.name()]()