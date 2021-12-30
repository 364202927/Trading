import abc
from util.utilities import err

class baseTactics(metaclass=abc.ABCMeta):
	'策略基类'
	_ex = None
	_upDateTime = 0  #update时间
	_signalTime = 0  #信号时间

	_allData = []   #读取到的数据
	_news = [] 	  	#记录各种指标

	def __init__(self, ex):
		if ex == None:
			err("交易所不能为空")
			return
		self._ex = ex
		self._upDateTime = 1
		self._signalTime = 5

	@abc.abstractmethod
	def info(self):
		pass

	@abc.abstractmethod
	def registerPlan(self):
		pass

	@abc.abstractmethod
	def signal(self):
		pass

	@abc.abstractmethod
	def updata(self):
		pass
	
	def getTime(self):
		return self._upDateTime, self._signalTime


	#~~~~~~~~~~~~
	def _setData(self,data):
		self._allData = data
		self._news = self._copyData(data)

	def _copyData(self, data):
		newData = data.copy()
		# newData.drop(['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_volume'], axis=1, inplace=True)
		return newData

	def _pdData(self):
		return self._ex.pd()
	
