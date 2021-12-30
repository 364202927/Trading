import os,time
import pandas as pd
from util.utilities import *

CSV_Path = "data/output/"
H5_Path = "data/h5/"

#自定义数据的key参数名
kHeadIndex = 'candle_begin_time' #data第一行的index
kUtc = 'utc'					 #utc时间参数
kSaveData = 'saveData'			 #fildata list类型
kKey = 'key'					 #读取h5的key

#pd显示
# pd.set_option('display.max_rows', None) #最大显示行
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

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
			self.__pdata = self.__pdata[[kHeadIndex,'open','high','low','close','volume']]#暂时只保存以下5个值，币安得数据会多给
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

		# 数据格式
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

	def dateCrop(self, data, beginTime, endTime):
		end_Time = data[kHeadIndex].iloc[-1] if endTime == 0 else endTime
		columns = data.columns
		newData = data[(data[columns[0]] >= self.datetime(beginTime)) &
						  (data[columns[0]] < self.datetime(end_Time))]
		newData.reset_index(inplace=True, drop=True)
		return newData

	def save2File(self, fileData, pdData = None, fileType = '.csv'):
		path = os.path.join(fileType == '.csv' and CSV_Path or H5_Path)
		fileName = path + fileData[-1] + fileType

		if pdData == None:
			pdData = self.__pdata
		if pdData.shape[0] == 0:
			err("保存失败：",fileName, "数据：", self.__pdata.shape[0])
			return
		if fileType == '.csv':
			# 检查路径,不存在则创建
			for file in fileData:
				path = os.path.join(path, file)
				if os.path.exists(path) is False:
					os.mkdir(path)
			pdData.to_csv(fileName, index=False)
		elif fileType == '.h5':
			pdData.to_hdf(fileName, key='data', mode='w')
		print("保存到文件：",fileName, "数据：", self.__pdata.shape[0])

	# def loadFile(self, fileName:str, cycle = '15T', beginTime = '2018-01-01', endTime = 0, isKlineData = True, **kw):
	def loadFile(self, fileName:str, cycle = '', beginTime = '2018-01-01', endTime = 0, **kw):
		def read_H5():
			h5_store = pd.HDFStore(H5_Path + fileName, mode='r')
			key = kw.get(kKey) if kw.get(kKey) else h5_store.keys()[0]
			self.__pdata = h5_store[key]
			h5_store.close()

		def read_Csv():
			self.__pdata = pd.read_csv(filepath_or_buffer = fileName,
										encoding='gbk',
										parse_dates=[kHeadIndex])
		#logic
		if fileName.endswith('.csv'):
			read_Csv()
		elif fileName.endswith('.h5'):
			read_H5()
		else:
			err("请检查路径文件：", fileName)
			return
		# 排序、去重
		self.__pdata.sort_values(by=[kHeadIndex], inplace=True)
		self.__pdata.drop_duplicates(subset=[kHeadIndex], inplace=True)
		self.__pdata.reset_index(inplace=True, drop=True)
		columns = self.__pdata.columns
		# if isKlineData:
		# 	columns = ['Data', 'Open', 'High', 'Low', 'Close', 'Volume', 'Quote_volume']
		# 	self.__pdata.columns = columns
			# self.__pdata.set_index(self.__pdata['Data'], inplace=True)
		#按周期合并
		if cycle != '':
			# self.__pdata = self.__pdata.resample(rule= cycle, on='Data', label='left', closed='left').agg(
			self.__pdata = self.__pdata.resample(rule= cycle, on=columns[0], label='left', closed='left').agg(
						{columns[1]: 'first',
						columns[2]: 'max', 
						columns[3]: 'min', 
						columns[4]: 'last', 
						columns[5]: 'sum'})
						#, columns[6]: 'sum'})
			self.__pdata.dropna(subset=[columns[1]], inplace=True)  # 去除一天都没有交易的周期
			self.__pdata = self.__pdata[self.__pdata[columns[5]] > 0]  # 去除成交量为0的交易周期
			self.__pdata.reset_index(inplace=True)
		#剔除数据
		self.__pdata = self.dateCrop(self.__pdata, beginTime = beginTime, endTime = endTime)
		# if isKlineData:
			# self.__pdata.set_index(self.__pdata[columns[0]], inplace=True)
		return self.__pdata

	def merge(self, leftData, rightData):
		self.__pdata = pd.merge(leftData, rightData,
						left_on=leftData.columns[0],
						right_on=rightData.columns[0],
						suffixes=['_left', '_right'],
						how='left')
		return self.__pdata
