from information import information
from core.exchange import exchange

class assetsCenter(object):
	"用户资产"
	# _instance_lock = threading.Lock()
	__exchanges = {}

	def __new__(cls, *args, **kwargs):
		# if not hasattr(Singleton, "_instance"):
		#     with Singleton._instance_lock:
		if not hasattr(assetsCenter, "_instance"):
			assetsCenter._instance = object.__new__(cls)
		return assetsCenter._instance

	def __init__(self):
		for name in information.keys():
			ex = exchange(name)
			self.__exchanges[name] = ex
		

	def getExchange(self, name:str = '')->object:
		if name == '':
			return self.__exchanges
		return self.__exchanges[name]

