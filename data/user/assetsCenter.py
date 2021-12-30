from information import information
from core.exchange import exchange
from util.utilities import err

class assetsCenter(object):
	"用户资产"
	# _instance_lock = threading.Lock()
	__instance = None
	__exchanges = {}

	def __new__(cls, *args, **kwargs):
		if cls.__instance:
			err("assetsCenter为单例对象，请使用use_ins")
			return cls.__instance
		cls.__instance = object.__new__(cls, *args, **kwargs)
		return cls.__instance  # 返回实例对象

	def __init__(self):
		for name in information.keys():
			ex = exchange(name)
			self.__exchanges[name] = ex
		

	def getExchange(self, name:str = '')->object:
		if name == '':
			return self.__exchanges
		return self.__exchanges[name]

#单例
user_ins = assetsCenter()

def exchange(name:str = ''):
	return user_ins.getExchange(name)