import os,time
import pandas as pd
from util.utilities import iso2Time

dataPath = "data/output/"
kHeadIndex = 'candle_begin_time'
kUtc = 'utc'
kSaveData = 'saveData'

# pd.set_option('display.max_rows', 10000) #最大显示行
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

#todo:未完成
#1.币安 合约格式化




class pdData:
	"pd数据处理和格式化"
	__pdata = None

	def __init__(self):
		pass

	def format(self, strType, data, *args, **kw):
		def candle(isFormat = True):
			if isFormat:
				self.__pdata = pd.DataFrame(data, dtype=float)			
			utc = 0
			if kw.get(kUtc): utc = kw[kUtc]
			self.__pdata.rename(columns={0: kHeadIndex, 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
			self.__pdata[kHeadIndex] = self.datetime(self.__pdata[kHeadIndex], other='ms', utc = utc)
			return True

		def candleConcat():
			tab = []
			for slice in data:
				tab.append(pd.DataFrame(slice,dtype=float))
			self.__pdata = pd.concat(tab, ignore_index=True)
			candle(False)
			self.__pdata.drop_duplicates(subset=[kHeadIndex], keep='last', inplace=True)
			self.__pdata.sort_values(kHeadIndex, inplace=True)
			self.__pdata = self.__pdata[(self.__pdata[kHeadIndex].dt.date >= self.datetime(args[0]).date()) &
										(self.__pdata[kHeadIndex].dt.date < self.datetime(args[1]).date())]
			return True

		def markets():
			pf = pd.DataFrame(data).T
			pf = pf[pf['symbol'].str.endswith('/USDT')]
			self.__pdata = list(pf['symbol'])
			return False

		# switch
		funTab = {
			'candle': candle,
			'candleConcat':candleConcat,
			'markets': markets,
		}
		if funTab.get(strType):
			if funTab[strType]():
				self.__pdata.reset_index(drop=True, inplace=True)
				# self.__pdata.set_index(HeadIndex, drop=True, inplace=True)
		# 保存到文件
		if kw.get(kSaveData):
			self.save2File(kw[kSaveData])

	def data(self):
		return self.__pdata

	def datetime(self, time, other=None, utc = 0):
		date = pd.to_datetime(time, unit=other)
		if utc > 0:
			date += pd.Timedelta(hours = utc)
		return date

	def save2File(self, fileData):
		path = os.path.join(dataPath)
		# 检查路径
		for i in range(len(fileData)-1):
			path = os.path.join(path, fileData[i])
			if os.path.exists(path) is False:
				os.mkdir(path)
		fileName = path + "/"+fileData[-1] + ".csv"
		print("保存到文件：",fileName, "数据：",self.__pdata.shape[0])
		if self.__pdata.shape[0] > 0:
			self.__pdata.to_csv(fileName,index=False)