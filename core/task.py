from util.utilities import *
from data.user.assetsCenter import *

kState = {
	'eActive':0, #待激活
	'eRun':1,	#正常运行
	'eStop':2,	 #停止
	'eWait':3,    #等待
}

class Task:
	'任务'   #__doc__ 查看标识

	__jobID = 0
	__isTest = False #测试盘
	__ex = None      #当前使用的交易所
	__state = kState['eActive'] #任务状态
	__strategyTab = []  #当前任务的策略
	__fnSetInterval = None  #定时器
	# todo那个币需要检测获取ticker,需记录检测币的数据，一种币触发一次信号
	# todo处理爆仓
	# todo处理期货或者现货
	# todo期货是否单向
	# 全仓or逐仓
	# 定义各交易所 手续费 期权等计算方式

	def __init__(self, allTactics, id, fnSetInterval):
		self.__strategy = allTactics
		self.__jobID = id
		self.__isTest = True
		self.__fnSetInterval = fnSetInterval

	def select(self, tactics:str, exName:str ,**kwargs):
		strategy = require('strategy.tactics.' + tactics)
		obj = strategy(exchange(exName))
		obj.registerPlan()
		self.__strategyTab.append(obj)

	#todo:参数回测，实盘回测
	def run(self, isTest = True):
		strInfo = "测试盘" if isTest == True else '实盘'
		log("任务："+ str(self.__jobID), strInfo, "。。。。。开始运行！", lv = 5)
		self.__isTest = isTest
		self.__state = kState['eWait'] if len(self.__strategyTab) == 0 else kState['eRun']
		if self.__state != kState['eRun']:
			return
		# 测试盘，固定为1秒触发一次信号, todo实盘按正常时间，还没做好
		for strategy in self.__strategyTab:
			upDateTime, signalTime = strategy.getTime()
			def fnCall():
				#todo:先获取到k线数据，再触发信号
				strategy.signal() #需要传入symbol检测
			self.__fnSetInterval(fnCall, seconds = (1 if isTest==True else signalTime))

	def updata(self,dt):
		pass

	def ID(self):
		return self.__jobID

	# 主线程，一直执行
	def upDate(self):
		if len(self.__strategy) == 0 or self.__state != kState['eRun']:
			return
		for strategy in self.__strategyTab:
			strategy.updata()