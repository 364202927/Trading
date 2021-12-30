from strategy.baseTactics import baseTactics
from util.utilities import *
import numpy as np

#todo:测试盘和实盘区别，后面再去修正
class boll(baseTactics):
	'布林线策略'

	#参数
	_maDay = 0  #n天均线
	_multipleStd = 0 #几倍的标准差

	def info(self):
		return "\n\n~~~描述~~~ \n收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过中轨的时候，平仓。\n收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过中轨的时候，平仓。\n\n"

	def registerPlan(self):
		self._upDateTime = 0.2
		self._signalTime = 15

		# 虚拟盘
		self._setData(self._pdData().loadFile('BTC-USDT_5m.h5', endTime = '2019-01-01', cycle = '15T', key = 'df'))
		# 均线
		self._maDay = 400
		self._multipleStd = 2
		self.testSignal()

		# log(self._news)

	def signal(self):
		pass


	def updata(self):
		pass

	# 计算均线和boll上下轨
	def bollTrack(self, maDay, multipleStd):
		#均线 = n天收盘价的 公式：a = 平均值(1+...)/n  b = sum((当前值-a)平方) c = 根号(b/(len - 1))
		self._news['median'] = self._allData['Close'].rolling(maDay,min_periods=1).mean()
		#上下轨 公式(当前值-均值)
		self._news['std'] = self._allData['Close'].rolling(maDay, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
		self._news['upper'] = self._news['median'] + multipleStd * self._news['std']
		self._news['lower'] = self._news['median'] - multipleStd * self._news['std']

	# 生成信号，测试框架
	def testSignal(self):
		#1.生成信号
		self.bollTrack(self._maDay, self._multipleStd)
		# 做多信号：当前K线的收盘价 > 上轨, 上一根k线少于上轨
		condition1 = self._allData['Close'] > self._news['upper']
		condition2 = self._allData['Close'].shift(1) <= self._news['upper'].shift(1)
		self._news.loc[condition1&condition2,'signal_long'] = 1
		# 做多平仓：由上向下穿过中轨
		condition1 = self._allData['Close'] < self._news['median']
		condition2 = self._allData['Close'].shift(1) >= self._news['median'].shift(1)
		self._news.loc[condition1&condition2,'signal_long'] = 0

		#做空 收盘价 < 下轨
		condition1 = self._allData['Close'] < self._news['lower']
		condition2 = self._allData['Close'].shift(1) >= self._news['lower'].shift(1)
		self._news.loc[condition1&condition2,'signal_short'] = -1
		# 做空平仓
		condition1 = self._allData['Close'] > self._news['median']
		condition2 = self._allData['Close'].shift(1) <= self._news['median'].shift(1)
		self._news.loc[condition1&condition2,'signal_short'] = 0

		#2.合并信号，去掉重复信号
		self._news['signal'] = self._news[['signal_long','signal_short']].sum(axis=1, min_count = 1, skipna=True)
		signal_pf = self._news[self._news['signal'].notnull()]['signal'] #获取不为空的信号
		signal_pf = signal_pf[signal_pf != signal_pf.shift(1)] #信号是重复的取消记录

		#3.填空缺少的信号 并用pos记录当前k线持仓状态
		self._news['signal'] = signal_pf
		self._news['signal'].fillna(method='ffill', inplace=True)
		self._news['signal'].fillna(value=0, inplace=True)  # 将初始行数的signal补全为0
		self._news['pos'] = self._news['signal'].shift()
		self._news['pos'].fillna(value=0, inplace=True)  # 将初始行数的pos补全为0

		#4.特殊处理 ok交易所4点进行的清算
		condition = (self._news['Data'].dt.hour == 16) & (self._news['Data'].dt.minute == 0)
		self._news.loc[condition, 'pos'] = None
		self._news['pos'].fillna(method='ffill', inplace=True) #此时间段不能买卖继续持有

		#5.列出开仓时间和下根k线时间
		self._news['open_next'] = self._news['Open'].shift(-1)
		self._news['open_next'].fillna(value=self._news['Close'], inplace=True)
		condition1 = self._news['pos'] != 0
		condition2 = self._news['pos'] != self._news['pos'].shift(1)#向上查
		self._news.loc[condition1 & condition2, 'buyTime'] = self._news['Data'] #买入信号
		self._news['buyTime'].fillna(method='ffill', inplace=True)
		self._news.loc[self._news['pos']==0, 'buyTime'] = 'NaT'
		# 去掉没用信息
		self._news.drop(['median', 'std', 'upper', 'lower', 'signal_long', 'signal_short',"signal"], axis=1, inplace=True)

		# 6.计算每单盈亏
		initial_cash = 10000  # 初始资金，默认为10000元
		face_value = 0.01  # btc是0.01，不同的币种要进行不同的替换
		c_rate = 5 / 10000  # 手续费，commission fees，默认为万分之5。不同市场手续费的收取方法不同，对结果有影响。比如和股票就不一样。
		slippage = 1 / 1000  # 滑点 ，可以用百分比，也可以用固定值。建议币圈用百分比，股票用固定值
		leverage_rate = 3 #杠杆倍数
		min_margin_ratio = 1 / 100  # 最低保证金率，低于就会爆仓
		# 张数 = 向下取整(initial_cash * leverage_rate /(face_value * open))
		# 开仓价 = open*(1 + pos * slippage)
		# 开仓后 要扣除手续费。在初始保证金中扣除 = initial_cash - 滑点 * face_value*开仓价 * c_rate
		self._news.loc[condition1 & condition2,'contract'] = np.floor(initial_cash * leverage_rate / (face_value * self._news['Open']))
		self._news.loc[condition1 & condition2, 'openPrice'] = self._news['Open'] * ( 1 + self._news['pos'] * slippage)
		self._news.loc[condition1 & condition2,'cash'] = initial_cash - self._news['openPrice'] * face_value * self._news['contract'] * c_rate
		tab=['contract','openPrice','cash']#向下赋值
		for key in tab:
			self._news[key].fillna(method='ffill', inplace=True)
		self._news.loc[self._news['pos'] == 0,tab] = None
		# 平仓价:滑点，手续费
		condition3 = self._news['pos'] != self._news['pos'].shift(-1) #向下查
		self._news.loc[condition1 & condition3, 'closePrice'] = self._news['open_next'] * ( 1 - self._news['pos'] * slippage)
		self._news.loc[condition1 & condition3, 'close_cash'] =  self._news['closePrice'] * face_value * self._news['contract'] * c_rate

		# 利润 = face_value * 张数 *（平仓价 - 开仓价）*pos
		# 用户净值 = cash + 利润
		
		# todo:缺数据赋值
		self._news.loc[condition1 & condition3, 'profit'] = face_value * self._news['contract'] * (self._news['closePrice']-self._news['openPrice'])*self._news['pos']
		self._news.loc[condition1 & condition3, 'netWorth'] = self._news['cash'] + self._news['profit']
		self._news['netWorth'] -= self._news['close_cash'] #平仓的手续费 
		# self._news.drop(['High', 'Low', 'Volume', 'Quote_volume'], axis=1, inplace=True)

		#7.至今持仓盈亏最小值
		self._news.loc[self._news['pos'] == 1, 'price_min'] = self._news['Low']
		self._news.loc[self._news['pos'] == -1, 'price_min'] = self._news['High']
		self._news['profit_min'] = face_value * self._news['contract'] * (self._news['price_min'] - self._news['openPrice']) * self._news['pos']
		# 账户净值最小值
		self._news['net_value_min'] = self._news['cash'] + self._news['profit_min']
		# 计算最低保证金率
		self._news['margin_ratio'] = self._news['net_value_min'] / (face_value * self._news['contract'] * self._news['price_min'])
		# 计算是否爆仓
		self._news.loc[self._news['margin_ratio'] <= (min_margin_ratio + c_rate), '是否爆仓'] = 1
		# 当下一根K线价格突变，在平仓的时候爆仓，要做相应处理。
		self._news.loc[condition1 & condition3 & (self._news['netWorth'] < 0), '是否爆仓'] = 1
		#8.涨跌幅
		self._news['equity_change'] = self._news['netWorth'].pct_change() #与上一个参数间百分比
		self._news.loc[condition1 & condition2, 'equity_change'] = self._news.loc[condition1 & condition2, 'netWorth'] / initial_cash - 1  # 开仓日的收益率
		self._news['equity_change'].fillna(value=0, inplace=True)
		self._news['equity_curve'] = (1 + self._news['equity_change']).cumprod() #累计的积
		# 记录到文件
		# merge = self._showMerge()
		# self._pdData().save2File(['data','h5', 'signal_btc'],merge)
		self._news.drop(['open_next', 'contract', 'openPrice', 'cash', 'closePrice', 'close_cash',
         'profit', 'price_min', 'profit_min', 'net_value_min', 'margin_ratio', '是否爆仓'], axis=1, inplace=True)
		print(self._news)

		# okex爆仓算法 1、币本位全仓爆仓价=【维持保证金率*总开仓张数+（开多张数-开空张数）】/（总亏损/面值+开多张数/开多均价-开空张数/开空均价）



