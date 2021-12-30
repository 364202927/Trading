import time, random
from apscheduler.schedulers.background import BackgroundScheduler
from inspect import isfunction

from util.utilities import *
from core.task import Task


kMaxTimer = 20 #最大支持定时器 个数
kTacticsPath = 'strategy/tactics'
kZone = 'Asia/Hong_Kong'

#事件通知，任务管理
class mainLoop:
	'主循环，定时器 管理'
	__instance = None
	__scheduler = None
	__timeHandle = {} 	#定时器句柄
	__taskDic = {} 		#全部任务
	__tacyicsFile = [] 	#全部策略文件

	def __new__(cls, *args, **kwargs):
		if cls.__instance:
			err("mainLoop为单例对象，请使用mainLoop_ins")
			return cls.__instance
		cls.__instance = object.__new__(cls, *args, **kwargs)
		return cls.__instance  # 返回实例对象

	def __init__(self):
		self.__timeHandle['count'] = 0
		self.__timeHandle['tabId'] = {}
		job_defaults = { 'max_instances': kMaxTimer }
		self.__scheduler = BackgroundScheduler(timezone= kZone, job_defaults=job_defaults)

	def showJob(self):
		pass

	def addJob(self): #任务状态
		def jobID():
			while True:
				id = random.randint(0, 10000)
				if not self.__taskDic.get(str(id)):
					return id
		#logic
		if len(self.__tacyicsFile) == 0:
			self.__tacyicsFile = path2File(kTacticsPath,'.py')
		ID = jobID()
		taskObj = Task(self.__tacyicsFile,ID, self.addInterval)
		self.__taskDic[ID] = taskObj
		return taskObj

	def clearJob(self, idOrObj = 0):
		id = idOrObj
		if type(idOrObj) != int:
			id = idOrObj.ID()
		if id == 0:
			self.__taskDic.clear()
			self.__taskDic = {}
		# 删除1个
		key = str(id)
		if self.__taskDic.get(key):
			del self.__taskDic[key]

	# hour =19 , minute ='23' seconds = '0' 这里表示每天的19：23 分执行任务
	# hour ='19-21', minute= '23' 表示 19:23、 20:23、 21:23 各执行一次任务
	# month='1,3,5,7-9', day='*',start_date='2018-01-10 09:30:00', end_date='2018-06-15 11:00:00'
	# interval固定，cron定时
	def addInterval(self, callFunc, timeType:str = 'interval', **kwargs):
		if not isfunction(callFunc):
			return
		self.__timeHandle['count'] += 1
		time_Id = "timeId_"+ str(self.__timeHandle['count'])
		self.__timeHandle['tabId'][time_Id] = True
		# log("添加定时器：", time_Id, self.__timeHandle['tabId'])
		self.__scheduler.add_job(callFunc, timeType, id = time_Id, **kwargs)
		if self.__timeHandle['count'] <= 1:
			self.__scheduler.start()
		return time_Id
	def clearTime(self, timeId = ''):
		if timeId == '':
			# for id in self.__timeHandle['tabId']:
				# self.__scheduler.remove_job(id)
			self.__timeHandle['count'] = 0
			self.__timeHandle['tabId'] = {}
			# todo：是否需要停止定时器
			return
		#删除一个
		if self.__timeHandle['tabId'][timeId] == 1:
			del self.__timeHandle['tabId'][timeId]
			self.__scheduler.remove_job(timeId)
		
	def start(self):
		while True:
			log("~~~main~~~~")
			# for key in self.__taskDic:
			# 	task = self.__taskDic[key]
			# 	task.updata()
			# 	print(self.__taskDic[key])


			time.sleep(1)

#Singleton
mainLoop_ins = mainLoop()

# 快捷调用
def setInterval(callFunc, timeType:str = 'interval', **kwargs):
    return mainLoop_ins.addInterval(callFunc, timeType, **kwargs)
def newJob():
	return mainLoop_ins.addJob()