from data.user.assetsCenter import user_ins
from util.pdData import pdData
from util.utilities import path2File
kOutPut = 'data/output/'

# binance
#获取btc 2020-01-01 ~ 2天后的数据
# ex_binance.historical_Candle('BTC/USDT', '2020-01-01', 2)
#获取btc 2020-01-01 ~ 2020-01-03的数据
# ex_binance.historical_Candle('BTC/USDT', '2020-01-01', '2020-01-02',save2File = True)
#获取多组，多时间间隔 数据
# ex_binance.historical_Candle(['BTC/USDT','ETH/USDT'], start_time = '2020-01-01', end_time = 5, timeFrameOrTab = ['30m'],save2File = True)
#交易所全文件记录到文件
# ex_binance.historical_Candle('all', start_time = '2020-01-01', timeFrameOrTab = '30m', save2File = True)
# okex
# ex_okex.historical_Candle(['BTC/USDT','ETH/USDT'], start_time = '2021-01-01', end_time = 5, timeFrameOrTab = ['15m','30m'], save2File = True)
# ex_okex.historical_Candle('all', '2021-01-01', '2021-01-02',save2File = True)
def historicalSpot(exName:str, symbolOrTab, start_time, end_time = 1, timeFrameOrTab = '30m'):
	ex = user_ins.getExchange(exName)
	ex.historical_Candle(symbolOrTab, start_time = start_time, end_time = end_time, timeFrameOrTab = timeFrameOrTab, save2File = True)

# 合约数据
# 币安 BTCUSDT BTCUSD_PERP   u本位币本位
# okex BTC-USDT-211210 交割  BTC-USDT-SWAP永续
def historicalFuture(exName:str, symbolOrTab, start_time, end_time = 1, timeFrameOrTab = '5m'):
	ex = user_ins.getExchange(exName)
	ex.fhistorical_Candle(symbolOrTab, start_time = start_time, end_time = end_time, timeFrameOrTab = timeFrameOrTab, save2File = True)

#整合对应交易所的文件到h5
def integrateCandel(exName:str):
	fileTab = path2File(kOutPut + exName,'.csv')
	pd = pdData()
	for file in fileTab:
		pd.loadFile(file['path'])
		strName = file['name']
		fileName = strName[:strName.find('-')]
		pd.save2File([fileName], fileType = '.h5')